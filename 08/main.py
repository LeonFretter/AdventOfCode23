import os
from tree import ProblemSet, Traversal, InstructionCircle, spawnMultiTraversal
from sys import argv


dirname = os.path.dirname(__file__)
inputfile = os.path.join(dirname, "input.txt")
args = argv[1:]

with open(inputfile) as f:
    lines = f.readlines()

    problem = ProblemSet(lines)

    start_node = problem.graph.getNode("AAA")
    end_node = problem.graph.getNode("ZZZ")

    traversal = Traversal(problem.graph, InstructionCircle(problem.instructions), start_node)
    while traversal.current != end_node:
        traversal.next()

    print(f"Part 1: {traversal.steps()}")

    start_nodes = problem.graph.getNodesWithDigit(2, "A")

    multi_traversal = spawnMultiTraversal(problem, start_nodes)

    while not all([node.getDigit(2) == "Z" for node in multi_traversal.currents]):
        multi_traversal.next()

    print(f"Part 2: {multi_traversal.steps}")
