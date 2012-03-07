import os
from StringIO import StringIO
import framecurve


def test_parser():
  data = "\r\n".join(["# Framecurve data", "10\t1293.12", "#Some useful info", "10\t145"])
  elements = framecurve.parse(StringIO(data))
  assert isinstance(elements, framecurve.Curve)

  assert len(elements) == 4

  assert isinstance(elements[0], framecurve.Comment)
  assert isinstance(elements[1], framecurve.FrameCorrelation)
  assert isinstance(elements[2], framecurve.Comment)
  assert isinstance(elements[3], framecurve.FrameCorrelation)

  assert elements[0].text == "Framecurve data"
  assert elements[1] == framecurve.FrameCorrelation(10, 1293.12)
  assert elements[2].text == "Some useful info"


def test_parse_with_neg_source_frame():
    data = "10\t-1293.12"
    elements = framecurve.Parser(StringIO(data)).parse()
    assert isinstance(elements, framecurve.Curve)

    assert len(elements) == 1
    assert isinstance(elements[0], framecurve.FrameCorrelation)
    assert framecurve.FrameCorrelation(10, -1293.12), elements[0]


def test_parse_with_neg_dest_frame():
    data = "-123\t-1293.12"
    elements = framecurve.parse(StringIO(data))
    assert isinstance(elements, framecurve.Curve)

    assert len(elements) == 1
    assert isinstance(elements[0], framecurve.FrameCorrelation)
    assert framecurve.FrameCorrelation(-123, -1293.12), elements[0]


def test_should_try_to_open_file_at_path_if_string_passed_to_parse():
    assert not os.path.exists("/tmp/some_file.framecurve.txt")
    try:
        framecurve.parse("/tmp/some_file.framecurve.txt")
    except IOError:
        pass
    else:
        assert False


def test_should_pick_file_path_from_passed_file_object():
    path = os.path.dirname(__file__) + "/fixtures/framecurves/sample_framecurve1.framecurve.txt"
    curve = framecurve.parse(open(path))
    assert "sample_framecurve1.framecurve.txt" == curve.filename


def test_parser_fails_on_malformed_lines():
    data = "Sachlich gesehen\nbambam"
    try:
        framecurve.parse(StringIO(data))
    except framecurve.MalformedError:
        pass
    else:
        assert False
