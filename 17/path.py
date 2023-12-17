from dataclasses import dataclass, field, InitVar
import sys


@dataclass
class Vec2:
    _x: InitVar[int]
    _y: InitVar[int]

    def __post_init__(self, x: int, y: int) -> None:
        self.__x = x
        self.__y = y

    @property
    def x(self) -> int:
        return self.__x

    @property
    def y(self) -> int:
        return self.__y

    def copy(self) -> "Vec2":
        return Vec2(self.x, self.y)

    def __add__(self, other: "Vec2"):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2"):
        return Vec2(self.x - other.x, self.y - other.y)

    def __eq__(self, other: "Vec2") -> bool:
        return self.x == other.x and self.y == other.y


@dataclass
class Node:
    pos: Vec2
    cost: int
    cost_to_reach: int = sys.maxsize


@dataclass
class PathCounter:
    """
        Counts how many consecutive steps in direction were taken
    """
    _direction: InitVar[Vec2]
    _count: InitVar[int]

    def __post_init__(self, direction: Vec2, count: int) -> None:
        self.__direction = direction
        self.__count = count

    @property
    def direction(self) -> Vec2:
        return self.__direction

    @property
    def count(self) -> int:
        return self.__count

    def copy(self) -> "PathCounter":
        return PathCounter(self.direction.copy(), self.count)


@dataclass
class Map:
    nodes: list[list[Node]] = field(default_factory=list)

    def node(self, pos: Vec2) -> Node:
        return self.nodes[pos.y][pos.x]

    def neighbors(self, node: Node) -> list[Node]:
        """
            Doesn't include diagonals
        """
        min_x = max(0, node.pos.x - 1)
        min_y = max(0, node.pos.y - 1)
        max_x = min(len(self.nodes[0]) - 1, node.pos.x + 1)
        max_y = min(len(self.nodes) - 1, node.pos.y + 1)
        neighbors = []
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if x == node.pos.x and y == node.pos.y:
                    continue
                if x == node.pos.x or y == node.pos.y:
                    neighbors.append(self.nodes[y][x])
        return neighbors

    def __str__(self) -> str:
        res = ""
        for row in self.nodes:
            row_str = ""
            for node in row:
                if node.cost_to_reach == sys.maxsize:
                    row_str += "X"
                else:
                    row_str += str(node.cost_to_reach)
                row_str += " "
            res += row_str + "\n"
        return res


def readMap(txt: str) -> Map:
    nodes = []
    for y, line in enumerate(txt.splitlines()):
        nodes.append([])
        for x, c in enumerate(line):
            nodes[y].append(Node(Vec2(x, y), int(c)))
    return Map(nodes)


def getNextNodes(m: Map, current: Node, current_cost_to_reach: int, visited: list[Node], counter: PathCounter, max_cost: int, highest_node_cost: int) -> list[tuple[Node, PathCounter]]:
    next_nodes: list[tuple[Node, PathCounter]] = []
    for neighbor in m.neighbors(current):
        new_cost_to_reach = current_cost_to_reach + neighbor.cost
        if new_cost_to_reach < neighbor.cost_to_reach + 4 * highest_node_cost and neighbor not in visited and new_cost_to_reach <= max_cost:
            direction = neighbor.pos - current.pos
            if counter.count < 3 or direction != counter.direction:
                new_counter = counter.copy()
                if direction == counter.direction:
                    new_counter = PathCounter(direction, counter.count + 1)
                else:
                    new_counter = PathCounter(direction, 1)

                if new_cost_to_reach < neighbor.cost_to_reach:
                    neighbor.cost_to_reach = new_cost_to_reach
                next_nodes.append((neighbor, new_counter))
    return next_nodes


def step(m: Map, current: Node, current_cost_to_reach: int, visited: list[Node], counter: PathCounter, max_cost: int, highest_node_cost: int) -> None:
    if current_cost_to_reach > max_cost:
        return
    print(m)
    new_visited = visited + [current]
    next_nodes = getNextNodes(m, current, current_cost_to_reach, new_visited, counter, max_cost, highest_node_cost)
    for next_node, next_counter in next_nodes:
        step(m, next_node, current_cost_to_reach + next_node.cost, new_visited, next_counter, max_cost, highest_node_cost),


def traverse(m: Map, max_cost: int) -> None:
    start = m.node(Vec2(0, 0))
    start.cost_to_reach = 0
    highest_node_cost = max([node.cost for row in m.nodes for node in row])
    step(m, start, 0, [start], PathCounter(Vec2(0, 0), 0), max_cost, highest_node_cost)


if __name__ == "__main__":
    txt = """\
2413432311323
3215453535623
3255245654254
3446585845452
4546657867536
1438598798454
4457876987766
3637877979653
4654967986887
4564679986453
1224686865563
2546548887735
4322674655533\
"""
    m = readMap(txt)
    traverse(m, 120)
