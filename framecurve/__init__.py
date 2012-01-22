import os
import re


__version__ = (0, 1)


EXTENSION = ".framecurve.txt"
SPEC_URL = "http://framecurve.org/specification"
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


def format_float(x):
    """Stringifies a float without trailing ".0" etc

    >>> str(1.0)
    '1.0'
    >>> str(1.000)
    '1.0'
    >>> format_float(1.0)
    '1'
    >>> format_float(1.000)
    '1'
    >>> format_float(1.1)
    '1.1'
    >>> format_float(1.0001)
    '1.0001'
    """

    x = str(x)
    return x.rstrip("0").rstrip(".")


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
        return "%d\t%s" % (self.at, format_float(self.value))

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
        self.fileobj = fileobj

    def parse(self):
        filepath = getattr(self.fileobj, "name", None)
        if filepath is None:
            filename = None
        else:
            filename = os.path.basename(filepath)

        cur = Curve(filename=filename)

        for i, line in enumerate(self.fileobj):
            line = line.decode("utf-8")

            # Remove trailing whitespace (and newlines etc)
            # TODO: Pednatically, trailing spaces weren't mentioned in the spec
            line = line.rstrip()

            m = self.COMMENT.match(line)
            if m is not None:
                cur.append(Comment(m.group(1).strip()))
                continue

            m = self.CORRELATION_RECORD.match(line)
            if m is not None:
                cur.append(FrameCorrelation(
                        at=int(m.group(1)),
                        value=float(m.group(2))))
                continue

            invalid_line_repr = repr(line).lstrip("u")
            raise MalformedError(
                "Malformed line %d: %s" % (i + 1, invalid_line_repr))

        return cur


class Validator(object):
    """Validates a framecurve file, according to
    http://framecurve.org/specification-v1.html

    >>> line1 = Comment("...")
    >>> line2 = FrameCorrelation(-22, 4.5)
    >>> c1 = Curve(values = [line1, line2])
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
    def ok(self):
        return len(self.warnings) == 0 and len(self.errors) == 0

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
    import StringIO
    return Parser(StringIO.StringIO(string)).parse()


def validate(fileobj):
    if isinstance(fileobj, basestring):
        fileobj = open(fileobj)

    return Validator(fileobj)


def validate_str(string):
    import StringIO
    return Validator(StringIO.StringIO(string))
