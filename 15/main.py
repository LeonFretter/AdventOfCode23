import os
from decode import decodeList, readList, readLensOps, LensBuckets

dirname = os.path.dirname(__file__)
filepath = os.path.join(dirname, 'input.txt')

with open(filepath) as f:
    txt = f.read()
    parts = readList(txt)
    part1 = decodeList(parts)
    print("Part 1: ", part1)

    ops = readLensOps(txt)
    buckets = LensBuckets()
    for op in ops:
        buckets.handle(op)

    part2 = buckets.calculateFocusingPower()
    print("Part 2: ", part2)
