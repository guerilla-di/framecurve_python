"""
def test_writes_preamble_if_needed():
    f = Framecurve.Curve.new(Framecurve.Tuple.new(10, 123))
    s = StringIO.new
    Framecurve.Serializer.new.serialize(s, f)
    assert "# http://framecurve.org/specification-v1\n# at_frame\tuse_frame_of_source\n10\t123.00000\r\n" == s.value()


def test_writes_only_existing_frames():
  f = Framecurve.Curve.new(Framecurve.Tuple.new(10, 123), Framecurve.Tuple.new(12, 456))
  s = StringIO.new
  
  Framecurve.Serializer.new.serialize(s, f)
  assert "# http://framecurve.org/specification-v1\n# at_frame\tuse_frame_of_source\n10\t123.00000\r\n12\t456.00000\r\n" == s.getvalue()


def test_validate_and_serialize_with_invalid_input():
  f = Framecurve.Curve.new
  s = StringIO()
  try:
      Framecurve.Serializer.new.validate_and_serialize(s, f)
  except framecurve.MalformedError:
      pass
  else:
      raise AssertionError("Expected MalformedError")
  


def test_validate_and_serialize_with_valid_input_works_without_errors():
  f = Framecurve.Curve.new(Framecurve.Tuple.new(10, 123))
  s = StringIO.new
  
  assert_nothing_raised { Framecurve.Serializer.new.validate_and_serialize(s, f) }
  assert_equal "# http://framecurve.org/specification-v1\n# at_frame\tuse_frame_of_source\n10\t123.00000\r\n", s.string

"""
