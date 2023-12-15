import os
from decode import decodeList, readList

dirname = os.path.dirname(__file__)
filepath = os.path.join(dirname, 'input.txt')

with open(filepath) as f:
    txt = f.read()
    parts = readList(txt)
    part1 = decodeList(parts)
    print("Part 1: ", part1)
