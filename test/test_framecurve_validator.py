import os
import framecurve
from StringIO import StringIO

from nose.plugins.attrib import attr


def test_should_error_out_with_malformed_input_to_parse_and_validate():
    v = framecurve.validate(StringIO("foobar"))
    assert len(v.errors) == 1
    print "errors", v.errors
    print "warnings", v.warnings
    assert v.errors == ["Malformed line 1: 'foobar'"]


def test_should_not_error_out_with_good_input_to_parse_and_validate():
    io = StringIO("# Nice framecurve\r\n1\t146.0")
    v = framecurve.validate(io)
    print "errors", v.errors
    print "warnings", v.warnings
    assert len(v.errors) == 0


def test_should_record_filename_error_with_improper_extension():
    with open("wrong.extension", "w") as f:
        f.write("# This might have been\r\n1\t123.45")

    try:
        v = framecurve.Validator(open("wrong.extension"))
        print "errors", v.errors
        print "warnings", v.warnings

        assert v.errors == [
            "The framecurve file must have the .framecurve.txt double extension, but was named 'wrong.extension'"]
    finally:
        os.unlink("wrong.extension")


def test_should_error_out_with_empty():
    s = StringIO("")
    v = framecurve.Validator(s)
    print "errors", v.errors
    print "warnings", v.warnings
    assert v.errors == [
        "The framecurve did not contain any lines at all",
        "The framecurve did not contain any frame correlation records"]


def test_should_error_out_without_actual_tuples():
    c = framecurve.Curve(values = [framecurve.Comment("Only text")])
    v = framecurve.Validator(curve = c)
    print "errors", v.errors
    print "warnings", v.warnings
    assert len(v.errors) == 1
    assert v.errors == ["The framecurve did not contain any frame correlation records"]


def test_should_error_out_with_dupe_frames():
    c = framecurve.Curve(values = [
            framecurve.FrameCorrelation(10, 123.4),
            framecurve.FrameCorrelation(10, 123.4)])

    v = framecurve.Validator(curve = c)
    print "errors", v.errors
    print "warnings", v.warnings
    assert len(v.errors) == 1
    assert v.errors == [
        "The framecurve contains the same frame (10) twice or more (2 times)"]


def test_should_error_out_with_improper_sequencing():
    c = framecurve.Curve(values = [
            framecurve.FrameCorrelation(10, 123.4), framecurve.FrameCorrelation(1, 123.4)])
    v = framecurve.Validator(curve = c)
    print "errors", v.errors
    print "warnings", v.warnings
    assert len(v.errors) == 1
    assert v.errors == [
        "The frame sequencing is out of order (expected [1, 10] but got [10, 1]). The framecurve spec mandates that frames are recorded sequentially"]


def test_should_error_out_with_neg_source_and_dest_values():
    c = framecurve.Curve(values = [
            framecurve.FrameCorrelation(-10, 123.4), framecurve.FrameCorrelation(1, -345.67)])
    v = framecurve.Validator(curve = c)
    print "errors", v.errors
    print "warnings", v.warnings
    errs = ["The line 1 had it's at_frame value (-10) below 1. The spec mandates at_frame >= 1.",
            "The line 2 had a use_frame_of_source value (-345.67000) below 0. The spec mandates use_frame_of_source >= 0."]
    assert not v.ok
    assert errs == v.errors


def test_parse_from_err_bad_extension():
    path = os.path.dirname(__file__) + "/fixtures/framecurves/incorrect.extension"
    v = framecurve.Validator(open(path))
    print "errors", v.errors
    print "warnings", v.warnings
    assert len(v.errors) == 1
    assert v.errors == [
        "The framecurve file must have the .framecurve.txt double extension, but was named 'incorrect.extension'"]


def test_parse_from_err_neg_frames():
    path = os.path.dirname(__file__) + "/fixtures/framecurves/err-neg-frames.framecurve.txt"
    v = framecurve.Validator(open(path))
    print "errors", v.errors
    print "warnings", v.warnings
    assert not v.ok
    assert len(v.errors) == 1
    assert v.errors == [
        "The line 3 had it's at_frame value (-1) below 1. The spec mandates at_frame >= 1."]


def test_parse_from_err_no_tuples():
    path = os.path.dirname(__file__) + "/fixtures/framecurves/err-no-tuples.framecurve.txt"
    v = framecurve.Validator(open(path))
    print "errors", v.errors
    print "warnings", v.warnings
    assert not v.ok
    assert len(v.errors) == 1
    assert v.errors == [
        "The framecurve did not contain any frame correlation records"]


def test_should_warn_without_preamble_url():
    c = framecurve.Curve(values = [framecurve.FrameCorrelation(10, 123.4)])
    v = framecurve.Validator(curve = c)
    print "errors", v.errors
    print "warnings", v.warnings
    assert v.ok
    assert not v.perfect
    assert len(v.warnings) > 0
    assert len(v.errors) == 0
    msg = "It is recommended that a framecurve starts with a comment with the specification URL, http://framecurve.org/specification"
    assert msg in v.warnings


def test_should_warn_without_preamble_headers():
    c = framecurve.Curve(values = [framecurve.Comment("http://framecurve.org/specification-v1"), framecurve.FrameCorrelation(10, 123.4)])
    v = framecurve.Validator(curve = c)
    print "errors", v.errors
    print "warnings", v.warnings
    assert v.ok
    assert not v.perfect
    assert len(v.warnings) > 0
    assert len(v.errors) == 0
    msg = "It is recommended for the second comment to provide a column header"
    assert msg in v.warnings


def test_should_parse_well():
    c = framecurve.Curve(values = [
            framecurve.Comment("http://framecurve.org/specification-v1"),
            framecurve.Comment("at_frame\tuse_frame_of_source"),
            framecurve.FrameCorrelation(10, 123.4)])
    v = framecurve.Validator(curve = c)
    assert v.ok
    assert len(v.warnings) == 0
    assert len(v.errors) == 0
