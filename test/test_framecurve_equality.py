import framecurve


def test_comment_equal():
    a = framecurve.Comment("a")
    a2 = framecurve.Comment("a")
    b = framecurve.Comment("b")

    assert a == a2
    assert a != b

    assert a is a
    assert a is not b


def test_framecorrelation_equal():
    a = framecurve.FrameCorrelation(at = 1, value = 2)
    a2 = framecurve.FrameCorrelation(at = 1, value = 2)
    b = framecurve.FrameCorrelation(at = 1, value = 2.5)

    assert a == a2
    assert a != b

    assert a is a
    assert a is not b


def test_curve_equal():
    a = framecurve.Curve(values = [framecurve.Comment("a")])
    a2 = framecurve.Curve(values = [framecurve.Comment("a")])
    b = framecurve.Curve(values = [framecurve.Comment("b")])

    assert a == a2
    assert a != b

    assert a is a
    assert a is not b
