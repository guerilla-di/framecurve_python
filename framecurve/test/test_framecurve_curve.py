import framecurve

def test_empty():
    c = framecurve.Curve()
    assert len(c) == 0


def test_one_tuple():
    c = framecurve.Curve()
    c.append(framecurve.FrameCorrelation(1, 2.4))

    assert len(c) == 1
    assert c[0] == framecurve.FrameCorrelation(1, 2.4)
    assert str(c[0]) == "1\t2.4"


def test_init_with_values():
    e1 = framecurve.FrameCorrelation(1, 2.4)
    e2 = framecurve.Comment("Test")
    c = framecurve.Curve(values = [e1, e2])
    assert len(c) == 2
    assert c[1].text == "Test"
