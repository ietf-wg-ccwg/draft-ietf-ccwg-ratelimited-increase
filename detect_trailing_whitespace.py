import sys

try:
    infile = open(sys.argv[1], "r")
    lineNo = 1
    line = infile.readline()
    while line != '':
        if len(line) > 1 and line[-2]==' ':
            print("Trailing whitespace detected at line", lineNo)
        line = infile.readline()
        lineNo += 1
    infile.close()
except IOError:
    print("couldn't read the input file.")
