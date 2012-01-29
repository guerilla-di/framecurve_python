import framecurve
import StringIO


def test_writes_preamble_if_needed():
    curve = framecurve.Curve(values = [framecurve.FrameCorrelation(10, 123)])
    expect = "# http://framecurve.org/specification-v1\r\n# at_frame\tuse_frame_of_source\r\n10\t123.00000\r\n"

    fileobj = StringIO.StringIO()
    framecurve.serialize(fileobj = fileobj, curve = curve)

    print repr(fileobj.getvalue())
    print repr(expect)
    assert fileobj.getvalue() == expect


def test_writes_only_existing_frames():
  curve = framecurve.Curve(values = [framecurve.FrameCorrelation(10, 123), framecurve.FrameCorrelation(12, 456)])
  expect = "# http://framecurve.org/specification-v1\r\n# at_frame\tuse_frame_of_source\r\n10\t123.00000\r\n12\t456.00000\r\n"
  s = StringIO.StringIO()
  framecurve.serialize(s, curve)

  print repr(expect)
  print repr(s.getvalue())
  
  assert s.getvalue() == expect


def test_validate_and_serialize_with_invalid_input():
  curve = framecurve.Curve()
  s = StringIO.StringIO()

  try:
      framecurve.Serializer(fileobj = s, curve = curve).validate_and_serialize()
  except framecurve.MalformedError:
      pass
  else:
      raise AssertionError("Expected MalformedError")


def test_validate_and_serialize_with_valid_input_works_without_errors():
    curve = framecurve.Curve(values = [framecurve.FrameCorrelation(10, 123)])
    expect = "# http://framecurve.org/specification-v1\r\n# at_frame\tuse_frame_of_source\r\n10\t123.00000\r\n"

    fileobj = StringIO.StringIO()

    framecurve.Serializer(fileobj = fileobj, curve = curve).validate_and_serialize()

    print repr(fileobj.getvalue)
    print repr(expect)
    assert fileobj.getvalue() == expect
