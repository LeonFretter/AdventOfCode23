import os
from tree import ProblemSet, Traversal, InstructionCircle

dirname = os.path.dirname(__file__)
inputfile = os.path.join(dirname, "input.txt")

with open(inputfile) as f:
    lines = f.readlines()

    problem = ProblemSet(lines)

    start_node = problem.graph.getNode("AAA")
    end_node = problem.graph.getNode("ZZZ")

    traversal = Traversal(problem.graph, InstructionCircle(problem.instructions), start_node)
    while traversal.current != end_node:
        traversal.next()

    print(f"Part 1: {traversal.steps()}")
