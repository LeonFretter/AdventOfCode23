from dataclasses import dataclass
from typing import Callable


@dataclass
class Node:
    name: str
    lhs: str
    rhs: str

    def __eq__(self, other: "Node") -> bool:
        return self.name == other.name

    def getDigit(self, idx: int) -> str:
        return self.name[idx]


NodePred = Callable[[Node], bool]


@dataclass
class Graph:
    nodes: list[Node]

    def getNode(self, name: str) -> Node:
        node = next(node for node in self.nodes if node.name == name)
        if node is None:
            raise Exception("Node not found")
        return node

    def goLeft(self, current: Node) -> Node:
        return self.getNode(current.lhs)

    def goRight(self, current: Node) -> Node:
        return self.getNode(current.rhs)

    def getNodesWithDigit(self, idx: int, digit: str) -> list[Node]:
        return [node for node in self.nodes if node.getDigit(idx) == digit]


def readNode(line: str) -> Node:
    value, rest = [x.strip() for x in line.split("=")]
    rest = rest.strip('()')
    lhs, rhs = [x.strip() for x in rest.split(",")]

    return Node(value, lhs, rhs)


def step(graph: Graph, current: Node, instructions: str) -> Node:
    if len(instructions) == 0:
        return current

    if instructions[0] == "L":
        return graph.goLeft(current)
    else:
        return graph.goRight(current)


class InstructionCircle:
    def __init__(self, instructions: str) -> None:
        self.instructions = instructions
        self.idx = 0

    def next(self) -> str:
        res = self.instructions[self.idx]
        self.idx = (self.idx + 1) % len(self.instructions)
        return res


class Traversal:
    def __init__(self, graph: Graph, instructions: InstructionCircle, current: Node) -> None:
        self.graph = graph
        self.instructions = instructions
        self.current = current
        self.path = [self.current]

    def next(self) -> Node:
        self.current = step(self.graph, self.current, self.instructions.next())
        self.path.append(self.current)
        return self.current

    def steps(self) -> int:
        return len(self.path) - 1


class MultiTraversal:
    def __init__(self, graph: Graph, instructions: InstructionCircle, starts: list[Node]) -> None:
        self.graph = graph
        self.instructions = instructions
        self.currents = starts
        self.steps = 0

    def next(self) -> list[Node]:
        next_instruction = self.instructions.next()
        self.currents = [step(self.graph, current, next_instruction) for current in self.currents]
        self.steps += 1
        return self.currents


class ProblemSet:
    def __init__(self, lines: list[str]) -> None:
        nonempty = [line.strip() for line in lines if len(line.strip()) > 0]
        self.instructions = nonempty[0]
        self.graph = Graph([readNode(line) for line in nonempty[1:]])


def spawnMultiTraversal(problem_set: ProblemSet, start_nodes: list[Node]) -> MultiTraversal:
    return MultiTraversal(problem_set.graph, InstructionCircle(problem_set.instructions), start_nodes)


if __name__ == "__main__":
    example_node = readNode("STS = (QBV, QVV)")
    assert example_node.name == "STS"
    assert example_node.lhs == "QBV"
    assert example_node.rhs == "QVV"

    example_txt = """
RL

AAA = (BBB, CCC)
BBB = (DDD, EEE)
CCC = (ZZZ, GGG)
DDD = (DDD, DDD)
EEE = (EEE, EEE)
GGG = (GGG, GGG)
ZZZ = (ZZZ, ZZZ)
"""
    example_lines = [line.strip() for line in example_txt.split("\n")]
    example = ProblemSet(example_lines)

    traversal = Traversal(example.graph, InstructionCircle(example.instructions), example.graph.getNode("AAA"))
    dst_node = example.graph.getNode("ZZZ")
    while traversal.current != dst_node:
        traversal.next()

    assert traversal.steps() == 2

    example_txt_2 = """
LLR

AAA = (BBB, BBB)
BBB = (AAA, ZZZ)
ZZZ = (ZZZ, ZZZ)
"""

    example_lines_2 = [line.strip() for line in example_txt_2.split("\n")]
    example_2 = ProblemSet(example_lines_2)
    traversal_2 = Traversal(example_2.graph, InstructionCircle(example_2.instructions), example_2.graph.getNode("AAA"))
    dst_node_2 = example_2.graph.getNode("ZZZ")
    while traversal_2.current != dst_node_2:
        traversal_2.next()

    assert traversal_2.steps() == 6

    example_txt_3 = """
LR

11A = (11B, XXX)
11B = (XXX, 11Z)
11Z = (11B, XXX)
22A = (22B, XXX)
22B = (22C, 22C)
22C = (22Z, 22Z)
22Z = (22B, 22B)
XXX = (XXX, XXX)
"""
    example_lines_3 = [line.strip() for line in example_txt_3.split("\n")]
    example_3 = ProblemSet(example_lines_3)

    start_nodes = example_3.graph.getNodesWithDigit(2, "A")
    multi_traversal = spawnMultiTraversal(example_3, start_nodes)

    while not all([node.getDigit(2) == "Z" for node in multi_traversal.currents]):
        multi_traversal.next()

    assert multi_traversal.steps == 6
