from dataclasses import dataclass


@dataclass
class Node:
    name: str
    lhs: str
    rhs: str

    def __eq__(self, other: "Node") -> bool:
        return self.name == other.name


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


class ProblemSet:
    def __init__(self, lines: list[str]) -> None:
        nonempty = [line.strip() for line in lines if len(line.strip()) > 0]
        self.instructions = nonempty[0]
        self.graph = Graph([readNode(line) for line in nonempty[1:]])


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
