from dataclasses import dataclass
from dig import Vec2, Instruction, Node


@dataclass
class VerticalLine:
    start: Vec2
    # negative if pointing upwards
    length: int

    @property
    def direction(self) -> Vec2:
        return Vec2(0, -1 if self.length < 0 else 1)

    @property
    def end(self) -> Vec2:
        return self.start + self.direction * self.length

    @property
    def is_upward(self) -> bool:
        return self.length < 0

    def get_point(self, t: int) -> Vec2:
        return self.start + self.direction * t

    def is_inside(self, pos: Vec2) -> bool:
        diff = pos - self.start
        if diff.x != 0:
            return False
        dist_y = diff.y
        if self.is_upward:
            return dist_y <= 0 and abs(dist_y) <= abs(self.length)
        else:
            return dist_y >= 0 and abs(dist_y) <= abs(self.length)


def readInstruction(line: str) -> Instruction:
    parts = line.split()
    part2 = parts[2].strip("()")
    part2 = part2[1:]

    dist_txt = part2[:-1]
    dir_txt = part2[-1]

    dist = int(dist_txt, 16)
    dir_idx = int(dir_txt, 16)

    directions = [
        Vec2(1, 0),
        Vec2(0, 1),
        Vec2(-1, 0),
        Vec2(0, -1),
    ]

    direction = directions[dir_idx]

    return Instruction(direction, dist)


def readInstructions(txt: str) -> list[Instruction]:
    return [readInstruction(line) for line in txt.splitlines()]


def getNodes(instructions: list[Instruction]) -> list[Node]:
    """
        These nodes build a path (representing a boundary).
        Path is guaranteed not to intersect itself.
        So path is either clockwise or counter-clockwise loop.
        If clockwise, then interior is on right.
        If counter-clockwise, then interior is on left.
    """
    current = Node(Vec2(0, 0))
    nodes = [current]
    for instruction in instructions:
        direction = instruction.direction
        dist = instruction.steps
        next_node = Node(current.pos + direction * dist)
        nodes.append(next_node)
        current = nodes[-1]
    # we assume that last node is beginning again
    return nodes[:-1]


@dataclass
class Point:
    pos: Vec2
    direction: Vec2
    considered: bool = False


def getInstructionPoints(instruction: Instruction, start_pos: Vec2) -> list[Point]:
    current = Point(start_pos, instruction.direction)
    points = [current]
    for i in range(1, instruction.steps + 1):
        next_pos = current.pos + instruction.direction * i
        points.append(Point(next_pos, instruction.direction))
    return points


def getVerticalBoundaryPoints(instructions: list[Instruction]) -> list[Point]:
    current = Point(Vec2(0, 0), Vec2(0, 0), True)
    points = []
    for instruction in instructions:
        instr_points = getInstructionPoints(instruction, current.pos)
        current = instr_points[-1]
        if instruction.direction.x == 0:
            points.extend(instr_points)
    return points


def sortVerticalBoundaryPoints(points: list[Point]) -> dict[int, list[Point]]:
    res: dict[int, list[Point]] = {}
    for p in points:
        if p.pos.y not in res:
            res[p.pos.y] = []
        res[p.pos.y].append(p)
    for row in res.values():
        row.sort(key=lambda p: p.pos.x)
    return res


def getVerticalLines(nodes: list[Node]) -> list[VerticalLine]:
    lines = []
    for i in range(len(nodes)):
        node1 = nodes[i]
        node2 = nodes[(i + 1) % len(nodes)]
        if node1.pos.x != node2.pos.x:
            continue
        length = node2.pos.y - node1.pos.y
        lines.append(VerticalLine(node1.pos, length))
    return lines


def isClockwise(nodes: list[Node]) -> bool:
    """
        see: https://stackoverflow.com/questions/1165647/how-to-determine-if-a-list-of-polygon-points-are-in-clockwise-order
        we sum over edges (x_{i+1} - x_i)*(y_{i+1} + y_i)
        if result is positive, then clockwise
        if result is negative, then counter-clockwise

        clockwise means that right of traversal is interior
        counter-clockwise means that left of traversal is interior
    """
    s = 0
    for i in range(len(nodes)):
        node1 = nodes[i]
        node2 = nodes[(i + 1) % len(nodes)]
        dx = node2.pos.x - node1.pos.x
        dy = node2.pos.y + node1.pos.y
        s += dx * dy
    # our coordinate system has positive y pointing down
    # for positive y pointing up, condition would be s > 0
    return s < 0


def getInteriorDirection(walk_direction: Vec2, clockwise: bool) -> Vec2:
    """
        Direction orhogonal to walk_direction,
        pointing to interior of path.
    """
    if clockwise:
        # pointing right of walk_direction
        # walking up -> pointing right
        # walking down -> pointing left
        return Vec2(-walk_direction.y, 0)
    else:
        return Vec2(walk_direction.y, 0)


@dataclass
class HorizontalRay:
    start: Vec2
    is_left: bool

    def getCollision(self, line: VerticalLine) -> Vec2 | None:
        ray_y = self.start.y
        line_x = line.start.x

        if self.is_left:
            if line_x > self.start.x:
                return None
            collision_point = Vec2(line_x, ray_y)
            if not line.is_inside(collision_point):
                return None
            return collision_point
        else:
            if line_x < self.start.x:
                return None
            collision_point = Vec2(line_x, ray_y)
            if not line.is_inside(collision_point):
                return None
            return collision_point


def createHorizontalInteriorRay(current_pos: Vec2, walk_direction: Vec2, clockwise: bool) -> HorizontalRay:
    assert walk_direction in [Vec2(0, 1), Vec2(0, -1)], "walk_direction must be vertical"
    ray_direction = getInteriorDirection(walk_direction, clockwise)
    ray_start = current_pos + ray_direction
    return HorizontalRay(ray_start, ray_direction == Vec2(-1, 0))


def traverseVerticalBoundary(points: dict[int, list[Point]], vertical_lines: list[VerticalLine], clockwise: bool) -> int:
    """
        Points must be a dict mapping y-coordinates to a list of points (a row).
        Each row must be sorted by x-coordinate.
    """
    res = 0
    i = 0
    total_count = sum(len(row) for row in points.values())
    for row in points.values():
        for p in row:
            if p.considered:
                continue
            p.considered = True
            if i % 1000 == 0:
                print(f"i: {i} of {total_count}, current-res: {res}")
            i += 1
            ray = createHorizontalInteriorRay(p.pos, p.direction, clockwise)
            found = False
            # we want to find closest hitting line
            vertical_lines = sorted(vertical_lines, key=lambda line: abs(line.start.x - p.pos.x))
            for line in vertical_lines:
                if found:
                    break
                collision = ray.getCollision(line)
                if collision is not None:
                    found = True
                    for other_p in row:
                        if other_p.pos == collision:
                            diff = other_p.pos - p.pos
                            res += abs(diff.x)
                            other_p.considered = True
                            break
                        elif other_p.pos.x > collision.x:
                            raise Exception("No boundary point found for collision")
            if not found:
                raise Exception("No collision found")
    return res


def countBoundary(nodes: list[Node]) -> int:
    res = 0
    for i in range(len(nodes)):
        node1 = nodes[i]
        node2 = nodes[(i + 1) % len(nodes)]
        diff = node2.pos - node1.pos
        res += abs(diff.x) + abs(diff.y) - 1
    return res


def countHorizontalBoundary(nodes: list[Node]) -> int:
    res = 0
    for i in range(len(nodes)):
        node1 = nodes[i]
        node2 = nodes[(i + 1) % len(nodes)]
        diff = node2.pos - node1.pos
        if diff.y == 0:
            res += abs(diff.x) - 1
    return res


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
    boundary_len = countBoundary(nodes)
    horizontal_boundary_len = countHorizontalBoundary(nodes)
    print("boundary len: " + str(boundary_len))
    print("horizontal boundary len: " + str(horizontal_boundary_len))
    res = ""
    for node in nodes:
        res += str(node) + ","
    print(res)

    print(len(instructions))

    clockwise = isClockwise(nodes)
    boundary = getVerticalBoundaryPoints(instructions)

    sorted_boundary = sortVerticalBoundaryPoints(boundary)
    boundary.clear()  # free up some memory
    vertical_lines = getVerticalLines(nodes)

    res = traverseVerticalBoundary(sorted_boundary, vertical_lines, clockwise)
    alt_res = res + horizontal_boundary_len
    print(res)
    print("alt: " + str(alt_res))
    assert res == 952408144115
# 952406015801
