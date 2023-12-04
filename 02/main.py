from solution import possibleIndicesSum, readGame, findPowerSum
import os

dirname = os.path.dirname(__file__)
inputFile = os.path.join(dirname, 'input.txt')


with open(inputFile, 'r') as f:
    lines = f.readlines()
    lines = [line.strip() for line in lines]

    games = [readGame(line) for line in lines]

    s = possibleIndicesSum(games)
    print(f"Part 1: {s}")

    s2 = findPowerSum(games)
    print(f"Part 2: {s2}")
