[framecurve](http://framecurve.org) file handling library for Python.

Includes a parser, validator and serialiser

## Basic usage

To load a Framecurve file:

    >>> import framecurve
    >>> curve = framecurve.parse(open("framecurve/test/fixtures/framecurves/sample_framecurve1.framecurve.txt"))

The `curve` is basically a list of all the records stored in the file,
including comments and so on:

    >>> for record in curve:
    ...    print repr(record)
    Comment(u'http://framecurve.org/specification-v1')
    Comment(u'at_frame\tuse_frame_of_source')
    FrameCorrelation(at=1, value=1.0)
    FrameCorrelation(at=5, value=12.34)
    FrameCorrelation(at=9, value=15.678)
    FrameCorrelation(at=15, value=25.764)

Or loop over all the FrameCorrelation records:

    >>> for record in curve.frames():
    ...    print repr(record)
    FrameCorrelation(at=1, value=1.0)
    FrameCorrelation(at=5, value=12.34)
    FrameCorrelation(at=9, value=15.678)
    FrameCorrelation(at=15, value=25.764)


You can also load a Framecurve by specifying a path (although passing a file-like object is recommended):

    >>> from_path = framecurve.parse("framecurve/test/fixtures/framecurves/sample_framecurve1.framecurve.txt")

Or from a string containing a Framecurve:

    >>> from_str = framecurve.parse_str("23\t35.5")

## Validating a curve

You can then validate a framecurve.Curve is valid:

    >>> v = framecurve.validate(curve = curve)
    >>> v.ok
    True

The `framecurve.validate_*` methods are similar to the `parse`
methods, you can also validate a file-like object:

    >>> v = framecurve.validate(open("framecurve/test/fixtures/framecurves/sample_framecurve1.framecurve.txt"))
    >>> v.ok
    True

Or a string:

    >>> v = framecurve.validate_str("23\t35.5")
    >>> v.errors
    []

## Creating a Framecurve from scratch

First, create a Curve object:

    >>> curve1 = framecurve.Curve()

Then append Comment's, FrameCorrelation's and such:

    >>> c1 = framecurve.FrameCorrelation(at = 23, value = 55.25)
    >>> curve1.append(c1)
    >>> c2 = framecurve.Comment("A comment!")
    >>> curve1.append(c2)
    >>> c3 = framecurve.FrameCorrelation(at = 24, value = 56)
    >>> curve1.append(c3)

You can also construct a Curve object with a list of objects:

    >>> curve2 = framecurve.Curve(values = [c1, c2, c3])

These are identical:

    >>> print curve1
    [FrameCorrelation(at=23, value=55.25), Comment('A comment!'), FrameCorrelation(at=24, value=56)]
    >>> print curve2
    [FrameCorrelation(at=23, value=55.25), Comment('A comment!'), FrameCorrelation(at=24, value=56)]


This curve can then be validated:

    >>> v = framecurve.validate(curve = curve1)
    >>> v.errors
    []


..and then serialized to a string, like so:

    >>> print framecurve.serialize_str(curve = curve1)
    # http://framecurve.org/specification-v1
    # at_frame  use_frame_of_source
    23  55.25000
    # A comment!
    24  56.00000


...or to a file-like object (e.g from `open("myfile.framecurve.txt", "w+")` or a StringIO):

    >>> import StringIO
    >>> fileobj = StringIO.StringIO()
    >>> framecurve.serialize(fileobj = fileobj, curve = curve1)
    >>> print fileobj.getvalue()
    # http://framecurve.org/specification-v1
    # at_frame  use_frame_of_source
    23  55.25000
    # A comment!
    24  56.00000

## Simplifying the curves

When Framecurves are baked out it might happen that they are clogged with values on linear segments,
where no change in timewarp speed occurs yet there are keyframes. To get rid of these intermediate keyframes,
run a reduction pass using `simplify`:

    >>> curve = framecurve.Curve()
    >>> c1 = framecurve.FrameCorrelation(at=1, value=2.4)
    >>> c2 = framecurve.FrameCorrelation(at=2, value=2.5)
    >>> c3 = framecurve.FrameCorrelation(at=3, value=2.6)
    >>> curve.append(c1)
    >>> curve.append(c2)
    >>> curve.append(c3)
    >>> 
    >>> framecurve.simplify(curve)
    [FrameCorrelation(at=1, value=2.4), FrameCorrelation(at=3, value=2.6)]

Make a habit of doing this when importing Framecurve files into your package.

## Testing the library

Install `nose` (via `pip` or otherwise) and run `nosetests` in the library directory.
