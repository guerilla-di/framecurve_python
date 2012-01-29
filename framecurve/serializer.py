from .common import MalformedError, SPEC_URL, COLUMN_HEADER
from .curvedata import Comment
from .validator import Validator


def has_preamble(curve):
    if len(curve) < 2:
        return False

    first = curve[0]
    second = curve[0]

    if not isinstance(first, Comment) or not isinstance(second, Comment):
        return False

    if SPEC_URL not in first.text:
        return False

    if COLUMN_HEADER not in second.text:
        return False

    return True


class Serializer(object):
    def __init__(self, fileobj, curve):
        self.fileobj = fileobj
        self.curve = curve

    def write_preamble(self):
        """Ensure the curve contains the specification
        """
        self.fileobj.write("# http://framecurve.org/specification-v1\r\n")
        self.fileobj.write("# at_frame\tuse_frame_of_source\r\n")

    def serialize(self):
        if not has_preamble(self.curve):
            self.write_preamble()

        for record in self.curve:
            self.fileobj.write("%s\r\n" % (record, ))

    def validate_and_serialize(self):
        v = Validator(curve = self.curve)
        if len(v.errors) > 0:
            raise MalformedError("Will not serialize a malformed curve: %s" % (
                    ", ".join(v.errors)))

        self.serialize()
