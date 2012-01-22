if __name__ == '__main__':
    import sys
    import framecurve
    fc = framecurve.Parser(
        open(sys.argv[1])).parse()
    print "\n".join([str(x) for x in fc])
