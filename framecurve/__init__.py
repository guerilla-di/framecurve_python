__version__ = (0, 1)


from .parser import Parser
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
    import StringIO
    return Parser(StringIO.StringIO(string)).parse()


def validate(fileobj):
    if isinstance(fileobj, basestring):
        fileobj = open(fileobj)

    return Validator(fileobj)


def validate_str(string):
    from . import validator
    import StringIO
    return validator.Validator(StringIO.StringIO(string))
