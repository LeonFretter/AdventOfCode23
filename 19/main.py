import os
from workflows import readProblemSet

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'input.txt')

with open(filename) as f:
    input_txt = f.read()

    problem_set = readProblemSet(input_txt)

    accepted = problem_set()

    part1 = sum(int(e) for e in accepted)
    print(f"Part 1: {part1}")
