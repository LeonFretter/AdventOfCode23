from dataclasses import dataclass


@dataclass
class Vec2:
    x: int
    y: int

    def __eq__(self, other: "Vec2") -> bool:
        return self.x == other.x and self.y == other.y

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, other: int) -> "Vec2":
        return Vec2(self.x * other, self.y * other)

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"


@dataclass
class Node:
    pos: Vec2

    def __str__(self) -> str:
        return str(self.pos)


@dataclass
class Instruction:
    direction: Vec2
    steps: int

    def getNodes(self, current: Node) -> list[Node]:
        nodes = []
        for i in range(1, self.steps + 1):
            nodes.append(Node(current.pos + self.direction * i))
        return nodes

    def __str__(self) -> str:
        return f"{self.direction} * {self.steps}"


def readInstruction(line: str) -> Instruction:
    parts = line.split()
    dir_txt = parts[0]
    direction = {
        "U": Vec2(0, 1),
        "D": Vec2(0, -1),
        "L": Vec2(-1, 0),
        "R": Vec2(1, 0),
    }[dir_txt]
    steps_txt = parts[1]
    steps = int(steps_txt)

    return Instruction(direction, steps)


def readInstructions(txt: str) -> list[Instruction]:
    return [readInstruction(line) for line in txt.splitlines()]


def shiftNodes(nodes: list[Node]) -> list[Node]:
    min_x = min(node.pos.x for node in nodes)
    min_y = min(node.pos.y for node in nodes)
    return [Node(Vec2(node.pos.x - min_x, node.pos.y - min_y)) for node in nodes]


def getNodes(instructions: list[Instruction]) -> list[Node]:
    nodes = []
    current = Node(Vec2(0, 0))
    for instruction in instructions:
        nodes.extend(instruction.getNodes(current))
        current = nodes[-1]
    return shiftNodes(nodes)


@dataclass
class Map:
    points: list[list[bool]]

    def copy(self) -> "Map":
        return Map([row.copy() for row in self.points])

    def neighborPositions(self, pos: Vec2) -> list[Vec2]:
        min_x = max(0, pos.x - 1)
        min_y = max(0, pos.y - 1)
        max_x = min(len(self.points[0]) - 1, pos.x + 1)
        max_y = min(len(self.points) - 1, pos.y + 1)
        positions = [
            pos + Vec2(0, 1),
            pos + Vec2(0, -1),
            pos + Vec2(-1, 0),
            pos + Vec2(1, 0),
        ]
        return [p for p in positions if min_x <= p.x <= max_x and min_y <= p.y <= max_y]

    def __int__(self) -> int:
        return sum(sum(row) for row in self.points)

    def __str__(self) -> str:
        return "\n".join("".join("#" if p else "." for p in row) for row in self.points)

    def __getitem__(self, pos: Vec2) -> bool:
        return self.points[pos.y][pos.x]

    def __setitem__(self, pos: Vec2, value: bool):
        self.points[pos.y][pos.x] = value


def createBoundaryMap(nodes: list[Node]) -> Map:
    max_x = max(node.pos.x for node in nodes)
    max_y = max(node.pos.y for node in nodes)
    points = [[False for _ in range(max_x + 1)] for _ in range(max_y + 1)]
    for node in nodes:
        points[node.pos.y][node.pos.x] = True
    return Map(points)


def fillBoundaryMap(m: Map, interior_point: Vec2) -> Map:
    filled_map = m.copy()
    stack = [interior_point]

    while len(stack) > 0:
        pos = stack.pop()
        if filled_map[pos]:
            continue
        filled_map[pos] = True
        stack.extend(filled_map.neighborPositions(pos))
    return filled_map


if __name__ == "__main__":
    txt = """\
R 6 (#70c710)
D 5 (#0dc571)
L 2 (#5713f0)
D 2 (#d2c081)
R 2 (#59c680)
D 2 (#411b91)
L 5 (#8ceee2)
U 2 (#caa173)
L 1 (#1b58a2)
U 2 (#caa171)
R 2 (#7807d2)
U 3 (#a77fa3)
L 2 (#015232)
U 2 (#7a21e3)\
"""

    instructions = readInstructions(txt)
    nodes = getNodes(instructions)
    boundary_map = createBoundaryMap(nodes)
    print(str(boundary_map) + "\n")
    filled_map = fillBoundaryMap(boundary_map, Vec2(1, 3))
    print(filled_map)
    count = int(filled_map)
    assert count == 62
