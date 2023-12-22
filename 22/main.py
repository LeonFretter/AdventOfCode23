import os
from bricks import readBricks, BrickMap

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'input.txt')

with open(filename) as f:
    lines = f.readlines()
    bricks = readBricks(lines)
    brick_map = BrickMap(bricks)
    brick_map.run()
    disintegratable = brick_map.countDisintegratable()
    print(f"Part 1: {disintegratable}")
