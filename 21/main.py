import os
from steps import readMap

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, "input.txt")

with open(filename) as f:
    m = readMap(f.read())

    reachable = m.reachable(m.findStart(), 64)

    part1 = len(reachable)
    print(f"Part 1: {part1}")
