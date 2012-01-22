import optparse
import fileinput

import framecurve


def main():
    opter = optparse.OptionParser()
    opts, args = opter.parse_args()

    for fname in args:
        f = open(fname)
        v = framecurve.Validator(f)

        if v.ok:
            print "%s: ok" % fname

        else:
            print "%s: %d errors, %d warnings" % (
                fname,
                len(v.errors),
                len(v.warnings))

            for e in v.errors:
                print "ERROR: %s" % e
            for w in v.warnings:
                print "WARNING: %s" % w


if __name__ == '__main__':
    main()
