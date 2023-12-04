import os
from map import Map

dirname = os.path.dirname(__file__)
inputFile = os.path.join(dirname, 'input.txt')

with open(inputFile) as f:
    lines = f.read().splitlines()
    m = Map(lines)

    nums = [w.getNumber() for w in m.getNumbersAdjacentToSymbol()]
    res = sum(nums)

    print(f"Part 1: {res}")
