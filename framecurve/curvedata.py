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
