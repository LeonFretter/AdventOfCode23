import os
from mirrors import readBlocks, findBlockMirrors, calculateMirrorValue, clearSmudge, calculateCleanMirrorValue

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'input.txt')

with open(filename) as f:
    txt = f.read()
    blocks = readBlocks(txt)
    mirrors = [findBlockMirrors(block) for block in blocks]
    part1 = calculateMirrorValue(blocks)

    print("Part 1:", part1)

    # Part 2
    cleaned_blocks = [clearSmudge(block) for block in blocks]
    new_value = calculateCleanMirrorValue(cleaned_blocks)

    print("Part 2: ", new_value)
