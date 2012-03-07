import doctest
import framecurve


def test_docstrings():
    def _test_module(mod):
        failcount, testcount = doctest.testmod(mod)

        print "%s tests failed, %s tests in total" % (failcount, testcount)
        assert failcount == 0

    modules = [
        framecurve,
        ]

    for m in modules:
        yield _test_module, m
