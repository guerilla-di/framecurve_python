EXTENSION = ".framecurve.txt"
SPEC_URL = "http://framecurve.org/specification"
COLUMN_HEADER = "at_frame\tuse_frame_of_source"


class FramecurveError(Exception):
    pass


class MalformedError(FramecurveError):
    pass
