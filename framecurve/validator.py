from .common import MalformedError, EXTENSION, SPEC_URL, COLUMN_HEADER
from .curvedata import Comment, FrameCorrelation
from .parser import Parser


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