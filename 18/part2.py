from dig import Vec2, Instruction, Node


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
    return nodes


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
    res = ""
    for node in nodes:
        res += str(node) + ","
    print(res)
