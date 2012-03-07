#!/usr/bin/env python2

"""Framecurve file handling library

For more info, see http://framecurve.org

The Framecurve project is subject to MIT license
http://framecurve.org/scripts/#license
"""

from __future__ import with_statement

import os
import re


__version__ = (0, 1)

EXTENSION = ".framecurve.txt"
SPEC_URL = "http://framecurve.org/specification-v1"
COLUMN_HEADER = "at_frame\tuse_frame_of_source"


class FramecurveError(Exception):
    pass


class MalformedError(FramecurveError):
    pass


class Comment(object):
    """Represents a comment line

    From spec:

    A comment is a line starting with a hashmark (#).
    """

    def __init__(self, text):
        """``text`` should not include the leading # character
        """
        self.text = text

    def __repr__(self):
        return "Comment(%r)" % (self.text)

    def __str__(self):
        return self._to_framecurve()

    def _to_framecurve(self):
        v = "# " + self.text.replace("\n", "").replace("\r", "")
        return v

    def __eq__(self, other):
        return self.text == other.text


class FrameCorrelation(tuple):
    """From spec:

    A frame correlation record represents a correlation point in
    time expressed by two fields separated by a TAB character, having
    the format of

    [destination_frame_integer][TAB][source_frame_float][CRLF|LF]
    """

    def __new__(cls, at, value):
        return super(FrameCorrelation, cls).__new__(cls, (at, value))

    def __repr__(self):
        return "%s(at=%r, value=%r)" % (
            self.__class__.__name__,
            self.at,
            self.value)

    def __str__(self):
        return "%d\t%.05f" % (self.at, self.value)

    def __eq__(self, other):
        return self.at == other.at and self.value == self.value

    @property
    def at(self):
        return self[0]

    @property
    def value(self):
        return self[1]


class Curve(list):
    """Represents the FrameCurve, as a list of Comments and
    FrameCorrelation objects
    """

    def __init__(self, filename=None, values=None):
        """``filename`` is the name this curve represents

        ``values`` is an optional list of objects, which allows the
        Curve to be constructed like so:

        >>> line1 = Comment("...")
        >>> line2 = FrameCorrelation(2, 4.5)
        >>> Curve(values = [line1, line2])
        [Comment('...'), FrameCorrelation(at=2, value=4.5)]
        """

        self.filename = filename
        if values is not None:
            self.extend(values)

    def frames(self):
        for record in self:
            if isinstance(record, FrameCorrelation):
                yield record

    def __eq__(self, other):
        same_fname = self.filename == self.filename
        same_values = list.__eq__(self, other)

        return same_fname and same_values


class Parser(object):
    COMMENT = re.compile(r"^#(.+)$")
    CORRELATION_RECORD = re.compile(
        r"""
        ^([-]?\d+)            # -42 or 42
        \t                    # tab
        (
            [-]?(\d+(\.\d*)?) # "-1" or "1" or "1.0" or "1."
            |                 # or:
            \.\d+             # ".2"
        )
        ([eE][+-]?[0-9]+)?    # "1.2e3", "1.2e-3" or "1.2e+3"
        $
        """, re.VERBOSE)

    def __init__(self, fileobj):
        r"""fileobj is a file like object (from open() or StringIO etc)

        Call parse method to get a Curve object:

        >>> import StringIO
        >>> f = StringIO.StringIO("# A comment\r\n2\t3.5\r\n")
        >>> p = Parser(f)
        >>> type(p)
        <class 'framecurve.Parser'>
        >>> p.parse()
        [Comment(u'A comment'), FrameCorrelation(at=2, value=3.5)]
        """
        self.fileobj = fileobj

    def parse(self):
        filepath = getattr(self.fileobj, "name", None)
        if filepath is None:
            filename = None
        else:
            filename = os.path.basename(filepath)

        cur = Curve(filename=filename)

        for i, line in enumerate(self.fileobj):
            # From spec, "Each record might only contain valid UTF-8
            # codepoint sequences or ASCII as it's subset"
            line = line.decode("utf-8")

            # Remove trailing whitespace (and newlines etc)
            line = line.rstrip()

            m = self.COMMENT.match(line)
            if m is not None:
                cur.append(Comment(m.group(1).strip()))
                continue # next line

            m = self.CORRELATION_RECORD.match(line)
            if m is not None:
                cur.append(FrameCorrelation(
                        at=int(m.group(1)),
                        value=float(m.group(2))))
                continue # next line

            # Unmatched line, error
            invalid_line_repr = repr(line).lstrip("u")
            raise MalformedError(
                "Malformed line %d: %s" % (i + 1, invalid_line_repr))

        return cur


def _ensure_preamble(curve):
    """Ensure the curve contains the specification
    """

    import copy
    curve = copy.copy(curve)

    have_spec = False
    if len(curve) > 0 and isinstance(curve[0], Comment):
        have_spec = curve[0].text == SPEC_URL

    if not have_spec:
        curve.insert(0, Comment(SPEC_URL))

    have_header = False
    if len(curve) > 1 and isinstance(curve[1], Comment):
        have_header = curve[1].text == COLUMN_HEADER

    if not have_header:
        curve.insert(1, Comment(COLUMN_HEADER))

    return curve


class Serializer(object):

    def __init__(self, fileobj, curve):
        self.fileobj = fileobj
        self.curve = curve

    def serialize(self):
        with_preamble = _ensure_preamble(self.curve)

        for record in with_preamble:
            self.fileobj.write("%s\r\n" % (record, ))

    def validate_and_serialize(self):
        v = Validator(curve = self.curve)
        if len(v.errors) > 0:
            raise MalformedError("Will not serialize a malformed curve: %s" % (
                    ", ".join(v.errors)))

        self.serialize()


class Validator(object):
    """Validates a framecurve file, according to
    http://framecurve.org/specification-v1.html

    >>> import framecurve
    >>> line1 = Comment("...")
    >>> line2 = FrameCorrelation(-22, 4.5)
    >>> c1 = framecurve.Curve(values = [line1, line2])
    >>> v = Validator(curve = c1)
    >>> v.ok
    False
    >>> len(v.errors) > 0
    True
    >>> len(v.warnings) > 0
    True
    """

    def __init__(self, fileobj = None, curve = None):
        """Either a file object (from open(...) or StringIO.StringIO
        etc), or a Curve object
        """

        self.fileobj = fileobj

        self.warnings = []
        self.errors = []

        if fileobj is not None:
            self._validate_fileobj(fileobj)
        elif curve is not None:
            self._validate_crv(crv = curve)
        else:
            raise ValueError("Must supply either fileobj or curve")

    @property
    def perfect(self):
        return len(self.warnings) == 0 and len(self.errors) == 0

    @property
    def ok(self):
        return len(self.errors) == 0

    def _validate_fileobj(self, fileobj):
        p = Parser(self.fileobj)
        try:
            crv = p.parse()
        except MalformedError, e:
            self.errors.append(str(e))
        else:
            self._validate_crv(crv)

    def _validate_crv(self, crv):
        funcs = [getattr(self, x)
                 for x in dir(self)
                 if x.startswith("_verify_")
                 or x.startswith("_recommend")]

        for f in funcs:
            f(crv = crv)

    def _verify_at_least_one_line(self, crv):
        if len(crv) == 0:
            self.errors.append(
                "The framecurve did not contain any lines at all")

    def _verify_at_least_one_tuple(self, crv):
        tuples = [x for x in crv if isinstance(x, FrameCorrelation)]
        if len(tuples) == 0:
            self.errors.append(
                "The framecurve did not contain any frame correlation records")

    def _verify_filename(self, crv):
        if crv.filename is None:
            return # TODO: Is having no filename valid (from StringIO etc)? Warning?

        if not crv.filename.endswith(EXTENSION):
            self.errors.append(
                "The framecurve file must have the %s double extension, but was named %r" % (
                    EXTENSION,
                    crv.filename))

    def _verify_no_duplicate_records(self, crv):
        dupes = []
        tuples = [x for x in crv if isinstance(x, FrameCorrelation)]
        all_ats = [x.at for x in tuples]
        uniq_ats = set(all_ats)
        dupes = [(x, all_ats.count(x)) for x in sorted(uniq_ats) if all_ats.count(x) > 1]

        for dupe_frame, dupe_count in dupes:
            self.errors.append(
                "The framecurve contains the same frame (%d) twice or more (%d times)" % (
                    dupe_frame, dupe_count))

    def _verify_proper_sequencing(self, crv):
        tuples = [x for x in crv if isinstance(x, FrameCorrelation)]
        frame_numbers = [x.at for x in tuples]
        proper_sequence = sorted(frame_numbers)

        # TODO: Flatten sequences to 1-22 or 1-4,6-22 etc

        if frame_numbers != proper_sequence:
            self.errors.append(
                "The frame sequencing is out of order "
                "(expected %s but got %s)."
                " The framecurve spec mandates that frames are recorded sequentially" % (
                    proper_sequence,
                    frame_numbers))

    def _verify_non_negative_source_and_destination_frames(self, crv):
        for i, item in enumerate(crv):
            if not isinstance(item, FrameCorrelation):
                continue # skip

            line_no = i + 1

            if item.at < 1:
                self.errors.append(
                    "The line %d had it's at_frame value (%d) below 1. The spec mandates at_frame >= 1." % (line_no, item.at))
            elif item.value < 0:
                self.errors.append("The line %d had a use_frame_of_source value (%.5f) below 0. The spec mandates use_frame_of_source >= 0." % (line_no, item.value))

    def _recommend_proper_preamble(self, crv):
        if len(crv) > 0 and isinstance(crv[0], Comment) and SPEC_URL in crv[0].text:
            pass
        else:
            self.warnings.append(
                "It is recommended that a framecurve starts with a comment with the specification URL, %s" % (
                    SPEC_URL))

    def _recommend_proper_column_headers(self, crv):
        if len(crv) > 2 and isinstance(crv[1], Comment) and crv[1].text.strip() == COLUMN_HEADER:
            pass
        else:
            self.warnings.append(
                "It is recommended for the second comment to provide a column header")


def parse(fileobj):
    """Parse a file-like object or a file-path
    """
    if isinstance(fileobj, basestring):
        fileobj = open(fileobj)

    return Parser(fileobj).parse()


def parse_str(string):
    """Parse a string containing a Framecurve
    """
    import StringIO
    return Parser(StringIO.StringIO(string)).parse()


def validate(fileobj = None, curve = None):
    """Given a file-like object or a file-path, return a Validator
    object.

    The object has an "ok" property which is True if the curve is
    perfect (no errors or warnings).

    You can get a list of the errors and warnings from ".errors" and ".warnings"
    """

    if isinstance(fileobj, basestring):
        fileobj = open(fileobj)

    return Validator(fileobj = fileobj, curve = curve)


def validate_str(string):
    """Validates a string containing a Framecurve

    >>> v = validate_str("10\t23.2")
    >>> v.ok
    False
    >>> v.warnings
    []
    >>> v.errors
    ["Malformed line 1: '10    23.2'"]
    """
    import StringIO
    return Validator(fileobj = StringIO.StringIO(string))


def serialize(fileobj, curve):
    if isinstance(fileobj, basestring):
        fileobj = open(fileobj)

    s = Serializer(fileobj = fileobj, curve = curve)
    s.serialize()


def serialize_str(curve):
    import StringIO
    fileobj = StringIO.StringIO()
    s = Serializer(fileobj = fileobj, curve = curve)
    s.serialize()
    return fileobj.getvalue()
