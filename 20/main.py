import os
from pulse import connectNodes, CommandCenter

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, "input.txt")

with open(filename) as f:
    lines = f.read().splitlines()
    nodes = connectNodes(lines)
    cc = CommandCenter(nodes)
    cc.pressButtonMulti(1000)

    part1 = cc.countPulses()
    print(f"Part 1: {part1}")
