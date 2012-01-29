__version__ = (0, 1)


from .parser import Parser
from .serializer import Serializer
from .curvedata import Curve, Comment, FrameCorrelation
from .validator import Validator
from .common import MalformedError


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
    ["Malformed line 1: '10.2  23.5'"]
    """
    import StringIO
    return validator.Validator(fileobj = StringIO.StringIO(string))


def serialize(fileobj, curve):
    if isinstance(fileobj, basestring):
        fileobj = open(fileobj)

    s = Serializer(fileobj = fileobj, curve = curve)
    s.serialize()


def serialize_str(curve):
    import StringIO
    fileobj = StringIO.StringIO()
    s = Serializer(fileobj = fileobj, curve = curve)
    return fileobj.getvalue()
