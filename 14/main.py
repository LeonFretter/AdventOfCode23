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

    print("Part 1: ", weight)

    hist: list[Board] = []

    i = 0
    while i < 1000000000:
        if board in hist:
            idx = hist.index(board)
            # idx is 0 after this op
            hist = hist[idx:]
            break
        hist.append(board.copy())
        board.spinCycle()
        print("i: ", i)
        if i >= 1000000000 - 5:
            weight = board.getWeight()
            print("weight:", weight)
        i += 1

    idx = (1000000000 - i) % len(hist)
    board = hist[idx]
    weight = board.getWeight()

    print("Part 2: ", weight)
