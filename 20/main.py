import os
from pulse import connectNodes, CommandCenter

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, "input.txt")

with open(filename) as f:
    lines = f.read().splitlines()
    nodes = connectNodes(lines)
    cc = CommandCenter(nodes)

    # part 1
    # cc.pressButtonMulti(1000)
    # part1 = cc.countPulses()
    # print(f"Part 1: {part1}")

    # part 2
    # conditions = cc.conditionStr("rx")
    # print("\n".join(conditions))
    path_strs = cc.pathStr("rx")
    print("\n".join(path_strs))

    # part2 = cc.pressButtonUntil()
    # print(f"Part 2: {part2}")
