import os
from arrangements import readLine, createVariantLine

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, "input.txt")

with open(filename) as f:
    lines = [readLine(line) for line in f.readlines()]
    variant_lines = [createVariantLine(line) for line in lines]

    num_matches = [line.countMatches() for line in variant_lines]
    print(f"Part 1: {sum(num_matches)}")
