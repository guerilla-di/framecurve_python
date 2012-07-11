import os
import framecurve


def test_simplify_with_two_frames():
    e1 = framecurve.FrameCorrelation(1, 2.4)
    e2 = framecurve.FrameCorrelation(2, 2.5)
    e3 = framecurve.FrameCorrelation(3, 2.6)
    c = framecurve.Curve(values = [e1, e2, e3])
    
    simplified = framecurve.simplify(c)
    
    assert len(simplified) == 2
    
    assert simplified[0].at == 1
    assert simplified[1].at == 3
    assert simplified[0].value == 2.4
    assert simplified[1].value == 2.6
    
def test_simplify_with_big_file():
    path = os.path.dirname(__file__) + "/fixtures/framecurves/huge.framecurve.txt"
    curve = framecurve.parse(open(path))
    assert "huge.framecurve.txt" == curve.filename
    
    assert len(curve) == 102
    simplified = framecurve.simplify(curve)
    assert len(simplified) == 16

