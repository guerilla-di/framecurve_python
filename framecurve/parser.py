import os
import re

from .curvedata import Curve, Comment, FrameCorrelation
from .common import MalformedError


class Parser(object):
    COMMENT = re.compile(r"^#(.+)$")
    CORRELATION_RECORD = re.compile(
        r"""
        ^([-]?\d+)            # -42 or 42
        \t                    # tab
        (
            [-]?(\d+(\.\d*)?) # "-1" or "1" or "1.0" or "1."
            |                 # or:
            \.\d+             # ".2"
        )
        ([eE][+-]?[0-9]+)?    # "1.2e3", "1.2e-3" or "1.2e+3"
        $
        """, re.VERBOSE)

    def __init__(self, fileobj):
        self.fileobj = fileobj

    def parse(self):
        filepath = getattr(self.fileobj, "name", None)
        if filepath is None:
            filename = None
        else:
            filename = os.path.basename(filepath)

        cur = Curve(filename=filename)

        for i, line in enumerate(self.fileobj):
            line = line.decode("utf-8")

            # Remove trailing whitespace (and newlines etc)
            # TODO: Pednatically, trailing spaces weren't mentioned in the spec
            line = line.rstrip()

            m = self.COMMENT.match(line)
            if m is not None:
                cur.append(Comment(m.group(1).strip()))
                continue

            m = self.CORRELATION_RECORD.match(line)
            if m is not None:
                cur.append(FrameCorrelation(
                        at=int(m.group(1)),
                        value=float(m.group(2))))
                continue

            invalid_line_repr = repr(line).lstrip("u")
            raise MalformedError(
                "Malformed line %d: %s" % (i + 1, invalid_line_repr))

        return cur
