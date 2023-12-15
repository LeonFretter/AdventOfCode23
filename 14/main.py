import os
from tilt import Board

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'input.txt')

with open(filename) as f:
    txt = f.read()
    lines = txt.strip().split("\n")
    board = Board(lines)
    board.rollNorth()
    weight = board.getWeight()

    print("Part 1:", weight)

    for i in range(1000000000):
        board.spinCycle()
        if i >= 1000000000 - 5:
            weight = board.getWeight()
            print("weight:", weight)
        # if i % 100 == 0:
        print(i)
    print("Part 2:", weight)
