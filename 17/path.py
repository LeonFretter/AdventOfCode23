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

    def __eq__(self, other: "PathCounter") -> bool:
        return self.direction == other.direction and self.count == other.count


@dataclass
class Visitor:
    counter: PathCounter
    cost_to_reach: int


@dataclass
class Node:
    pos: Vec2
    cost: int
    cost_to_reach: int = sys.maxsize
    distance: int = sys.maxsize
    naive_cost: int = sys.maxsize
    visitors: list[Visitor] = field(default_factory=list)

    def accuCost(self, w=2) -> int:
        return self.cost + self.distance * w


def costToString(cost: int) -> str:
    if cost == sys.maxsize:
        return "X"
    else:
        return str(cost)


class Map:
    def __init__(self, nodes: list[list[Node]]) -> None:
        self.nodes = nodes
        goal_pos = self.nodes[len(self.nodes) - 1][len(self.nodes[0]) - 1].pos
        for row in self.nodes:
            for node in row:
                diff = goal_pos - node.pos
                node.distance = abs(diff.x) + abs(diff.y)
        self.goal_node = self.node(Vec2(len(self.nodes[0]) - 1, len(self.nodes) - 1))
        self.goal_node.naive_cost = 0
        self.mean_cost = sum([node.cost for row in self.nodes for node in row]) / (len(self.nodes) * len(self.nodes[0]))
        self.max_cost = max([node.cost for row in self.nodes for node in row])
        self.upper_bound_naive = self.max_cost * len(self.nodes) + len(self.nodes[0])
        self.w = len(self.nodes)
        self.h = len(self.nodes[0])

    def node(self, pos: Vec2) -> Node:
        return self.nodes[pos.y][pos.x]

    def assignNaiveCosts(self, current: Node) -> None:
        stack = [current]

        i = 0
        while stack:
            current = stack.pop()
            options = self.neighbors(current)
            for option in options:
                naive_cost = current.naive_cost + option.cost
                if option.naive_cost > naive_cost and naive_cost <= self.upper_bound_naive:
                    option.naive_cost = naive_cost
                    stack.append(option)
            i += 1
            if i % 10000 == 0:
                print("stack size: ", len(stack))

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

    def naiveCostsStr(self) -> str:
        res = ""
        for row in self.nodes:
            row_str = ""
            for node in row:
                row_str += costToString(node.naive_cost)
                row_str += " "
            res += row_str + "\n"
        return res

    def costToReachStr(self) -> str:
        res = ""
        for row in self.nodes:
            row_str = ""
            for node in row:
                row_str += costToString(node.cost_to_reach)
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


def readMapWithNaiveCosts(map_txt: str, naive_costs_txt: str) -> Map:
    nodes = []
    for y, line in enumerate(map_txt.splitlines()):
        nodes.append([])
        for x, c in enumerate(line):
            nodes[y].append(Node(Vec2(x, y), int(c)))
    m = Map(nodes)
    for y, line in enumerate(naive_costs_txt.splitlines()):
        for x, c in enumerate(line.split()):
            if c == "X":
                continue
            else:
                m.node(Vec2(x, y)).naive_cost = int(c)
    return m


def readMapWithCostToReach(map_txt: str, naive_costs_txt: str, cost_to_reach_txt: str) -> Map:
    nodes = []
    for y, line in enumerate(map_txt.splitlines()):
        nodes.append([])
        for x, c in enumerate(line):
            nodes[y].append(Node(Vec2(x, y), int(c)))
    m = Map(nodes)
    for y, line in enumerate(naive_costs_txt.splitlines()):
        for x, c in enumerate(line.split()):
            if c == "X":
                continue
            else:
                m.node(Vec2(x, y)).naive_cost = int(c)
    for y, line in enumerate(cost_to_reach_txt.splitlines()):
        for x, c in enumerate(line.split()):
            if c == "X":
                continue
            else:
                m.node(Vec2(x, y)).cost_to_reach = int(c)
    return m


def filterOptions(options: list[Node], current: Node, counter: PathCounter, upper_bound=sys.maxsize) -> list[Node]:
    # TODO: which fields can we really exclude?
    res = []
    highest_cycle_cost = 36
    for option in options:
        direction = option.pos - current.pos
        if option.cost_to_reach > upper_bound:
            continue
        new_cost = current.cost_to_reach + option.cost
        if new_cost > option.cost_to_reach + highest_cycle_cost:
            continue

        # if counter.count < 3 and option.naive_cost > current.naive_cost:
        #     continue

        # we can exclude options that have been visited by a visitor with a lower cost and the same counter
        # if any([visitor.counter == counter and visitor.cost_to_reach < current.cost_to_reach for visitor in option.visitors]):
        #     continue
        if counter.count < 3 or direction != counter.direction:
            res.append(option)
    return res


@dataclass
class NodeIt:
    node: Node
    counter: PathCounter
    path: list[Node] = field(default_factory=list)
    cost_to_traverse: int = 0


def traverse(m: Map, root_node: Node, upper_bound=sys.maxsize):
    root_node.cost_to_reach = 0
    stack = [NodeIt(root_node, PathCounter(Vec2(0, 0), 0), [root_node], 0)]
    goal_node = m.goal_node
    max_len = m.w + m.h * 2
    # cost of moving left three times

    i = 0
    while stack:
        current = stack.pop(len(stack) - 1)
        if goal_node.cost_to_reach < upper_bound:
            upper_bound = goal_node.cost_to_reach

        if len(current.path) > 3:
            previous = current.path[-2]
            two_before = current.path[-3]
            if current.node.naive_cost > previous.naive_cost and previous.naive_cost > two_before.naive_cost:
                continue

        options = m.neighbors(current.node)
        options = filterOptions(options, current.node, current.counter)

        # options = [option for option in options if option.cost_to_reach > current.cost_to_traverse + option.cost]
        options = reversed(sorted(options, key=lambda n: n.distance))

        for option in options:
            new_cost_to_traverse = current.cost_to_traverse + option.cost
            option.cost_to_reach = min(option.cost_to_reach, new_cost_to_traverse)
            direction = option.pos - current.node.pos
            new_counter = PathCounter(direction, current.counter.count + 1 if direction == current.counter.direction else 1)
            new_path = current.path + [option]
            new_node_it = NodeIt(option, new_counter, new_path, new_cost_to_traverse)
            # option.visitors.append(Visitor(new_counter, new_cost_to_traverse))
            stack.append(new_node_it)
        i += 1
        if i % 1000 == 0:
            print("stack size: ", len(stack))
            print("current lowest: ", m.goal_node.cost_to_reach)


def traverseFromStart(m: Map, upper_bound=sys.maxsize):
    traverse(m, m.node(Vec2(0, 0)), upper_bound)


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
    traverseFromStart(m)
    print(m.costToReachStr())
