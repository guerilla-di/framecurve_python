def test_init():
    import framecurve
    c = framecurve.Comment("Very interesting \r\n comment")
    assert c.text == "Very interesting \r\n comment"
    assert str(c) == "# Very interesting  comment"
    assert str(c) == c._to_framecurve()
