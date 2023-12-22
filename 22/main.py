import os
from bricks import readBricks, BrickMap, createTrees, treeFallCounts

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'input.txt')

with open(filename) as f:
    lines = f.readlines()
    bricks = readBricks(lines)
    brick_map = BrickMap(bricks)
    brick_map.run()
    disintegratable = brick_map.countDisintegratable()
    print(f"Part 1: {disintegratable}")

    # Part 2
    trees = createTrees(brick_map)
    fall_counts = treeFallCounts(trees)
    s = sum(fall_counts)
    print(f"Part 2: {s}")
