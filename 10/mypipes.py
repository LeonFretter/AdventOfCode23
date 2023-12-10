from dataclasses import dataclass
from enum import Enum
from typing import Optional


@dataclass
class Vec2:
    x: int
    y: int

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)

    def __eq__(self, other: "Vec2") -> bool:
        return self.x == other.x and self.y == other.y

    def __neg__(self) -> "Vec2":
        return Vec2(-self.x, -self.y)


NORTH = Vec2(0, -1)
EAST = Vec2(1, 0)
SOUTH = Vec2(0, 1)
WEST = Vec2(-1, 0)

type Direction = Vec2


@dataclass
class Field:
    pos: Vec2
    connections: list[Direction]
    is_start: bool = False
    is_main_loop: bool = False
    symbol: str = ""

    def getConnectionPositions(self) -> list[Vec2]:
        return [self.pos + x for x in self.connections]

    def getPotentialNeighborPositions(self) -> list[Vec2]:
        return [self.pos + x for x in [NORTH, EAST, SOUTH, WEST]]


@dataclass
class Map:
    fields: list[list[Field]]
    start_field: Field

    def getField(self, x: int, y: int) -> Field:
        return self.fields[y][x]

    def getNeighbors(self, field: Field) -> list[Field]:
        positions = field.getPotentialNeighborPositions()
        positions = [x for x in positions if x.x >= 0 and x.y >= 0 and x.y < len(self.fields) and x.x < len(self.fields[x.y])]
        return [self.getField(x.x, x.y) for x in positions]

    def getConnectionFields(self, field: Field) -> list[Field]:
        return [self.getField(x.x, x.y) for x in field.getConnectionPositions()]

    def getNextField(self, current: Field, last: Field) -> Field:
        candidates = self.getConnectionFields(current)
        candidates.remove(last)
        if len(candidates) == 0:
            raise Exception("No candidates found")
        next_field = candidates[0]
        return next_field


def connectStart(m: Map, start_field: Field) -> None:
    start_pos = start_field.pos
    neighbors_pos = [
        (NORTH, start_pos + NORTH),
        (EAST, start_pos + EAST),
        (SOUTH, start_pos + SOUTH),
        (WEST, start_pos + WEST),
    ]

    for direction, pos in neighbors_pos:
        if pos.x < 0 or pos.y < 0:
            continue
        if pos.y >= len(m.fields) or pos.x >= len(m.fields[pos.y]):
            continue
        field = m.getField(pos.x, pos.y)
        if -direction in field.connections:
            start_field.connections.append(direction)
    if NORTH in start_field.connections and SOUTH in start_field.connections:
        start_field.symbol = "|"
    elif EAST in start_field.connections and WEST in start_field.connections:
        start_field.symbol = "-"
    elif NORTH in start_field.connections and EAST in start_field.connections:
        start_field.symbol = "L"
    elif NORTH in start_field.connections and WEST in start_field.connections:
        start_field.symbol = "J"
    elif SOUTH in start_field.connections and WEST in start_field.connections:
        start_field.symbol = "7"
    elif SOUTH in start_field.connections and EAST in start_field.connections:
        start_field.symbol = "F"


def readField(char: str, pos: Vec2) -> Field:
    match char:
        case "|":
            return Field(pos, [NORTH, SOUTH], symbol=char)
        case "-":
            return Field(pos, [EAST, WEST], symbol=char)
        case "L":
            return Field(pos, [NORTH, EAST], symbol=char)
        case "J":
            return Field(pos, [NORTH, WEST], symbol=char)
        case "7":
            return Field(pos, [SOUTH, WEST], symbol=char)
        case "F":
            return Field(pos, [SOUTH, EAST], symbol=char)
        case ".":
            return Field(pos, [], symbol=char)
        case "S":
            return Field(pos, [], True, symbol=char)
        case _:
            raise Exception(f"Unknown character: {char}")


def readMap(lines: list[str]) -> Map:
    fields: list[list[Field]] = []
    start_field: Optional[Field] = None
    for y, line in enumerate(lines):
        fields.append([])
        for x, char in enumerate(line):
            field = readField(char, Vec2(x, y))
            if field.is_start:
                start_field = field
            fields[-1].append(field)
    if start_field is None:
        raise Exception("No start field found")
    res = Map(fields, start_field)
    connectStart(res, res.start_field)
    return res


@dataclass
class Node:
    field: Field
    parent: Optional["Node"] = None
    child: Optional["Node"] = None
    distance: int = -1


type Path = Node


def createLoop(m: Map) -> Path:
    current_field = m.start_field
    current_field.is_main_loop = True
    last_field = m.getConnectionFields(current_field)[0]
    current_node = Node(current_field)
    start_node = current_node

    next_field = m.getNextField(current_field, last_field)

    while next_field is not None and next_field is not m.start_field:
        next_node = Node(next_field, parent=current_node)
        current_node.child = next_node
        current_node = next_node
        last_field = current_field
        current_field = next_field
        current_field.is_main_loop = True
        next_field = m.getNextField(current_field, last_field)

    start_node.parent = current_node
    current_node.child = start_node

    return start_node


def assignDistances(start: Path) -> None:
    # forward
    current_node = start
    current_node.distance = 0
    while current_node.child is not start:
        current_node.child.distance = current_node.distance + 1
        current_node = current_node.child

    # backward
    current_node = start
    while current_node.parent is not start:
        current_node.parent.distance = min(current_node.distance + 1, current_node.parent.distance)
        current_node = current_node.parent


def unwrapLoop(loop: Path) -> list[Node]:
    res: list[Node] = []
    current_node = loop
    while current_node.child is not loop and current_node.child is not None:
        res.append(current_node)
        current_node = current_node.child
    res.append(current_node)
    return res


@dataclass
class AugmentedField:
    is_main_loop: bool
    is_pseudo: bool
    symbol: str = ""
    pos: Optional[Vec2] = None


class AugmentedMap:
    def __init__(self, m: Map) -> None:
        # TODO: handle S

        self.origin = m
        res: list[list[AugmentedField]] = []
        # rows
        for row in m.fields:
            res.append([])
            res_row = res[-1]
            for elem in row:
                res_row.append(AugmentedField(elem.is_main_loop, False, elem.symbol))
            res.append([])
            augmented_row = res[-1]
            for x, elem in enumerate(row):
                # all fields that go south
                if res_row[x].is_main_loop and res_row[x].symbol in ["|", "7", "F"]:
                    augmented_row.append(AugmentedField(True, True, "|"))
                else:
                    augmented_row.append(AugmentedField(False, True, "."))

        res_2: list[list[AugmentedField]] = []
        for row in res:
            res_2.append([])

        # columns
        for x in range(0, len(res[0])):
            res_column = [r[x] for r in res]
            augmented_column = []
            for y in range(0, len(res)):
                # augmented row
                if y % 2 == 1:
                    augmented_column.append(AugmentedField(False, True, "."))
                else:
                    # all fields that go east
                    if res_column[y].is_main_loop and res_column[y].symbol in ["-", "L", "F"]:
                        augmented_column.append(AugmentedField(True, True, "-"))
                    else:
                        augmented_column.append(AugmentedField(False, True, "."))

            for y in range(0, len(res)):
                res_2[y].append(res[y][x])
                res_2[y].append(augmented_column[y])

        self.fields = res_2
        for y, row in enumerate(self.fields):
            for x, elem in enumerate(row):
                elem.pos = Vec2(x, y)

    def __str__(self) -> str:
        res = ""
        for row in self.fields:
            for elem in row:
                res += elem.symbol
            res += "\n"
        return res

    def getNeighbors(self, elem: AugmentedField) -> list[AugmentedField]:
        positions = [elem.pos + x for x in [NORTH, EAST, SOUTH, WEST]]
        positions = [x for x in positions if x.x >= 0 and x.y >= 0 and x.y < len(self.fields) and x.x < len(self.fields[x.y])]
        return [self.fields[pos.y][pos.x] for pos in positions]


class NiceMap:
    def __init__(self, augmentedMap: AugmentedMap) -> None:
        self.origin = augmentedMap

    def __str__(self) -> str:
        res = ""
        for row in self.origin.fields:
            for elem in row:
                if elem.is_main_loop:
                    if elem.is_pseudo:
                        res += "0"
                    else:
                        res += "1"
                else:
                    if elem.is_pseudo:
                        res += "_"
                    else:
                        res += "."
            res += "\n"
        return res


type Region = list[AugmentedField]


class NiceRegion:
    def __init__(self, augmentedMap: AugmentedMap, region: Region) -> None:
        self.origin = augmentedMap
        self.region = region

    def __str__(self) -> str:
        res = ""
        for row in self.origin.fields:
            for elem in row:
                if elem in self.region:
                    res += "x"
                else:
                    if elem.is_main_loop:
                        if elem.is_pseudo:
                            res += "0"
                        else:
                            res += "1"
                    else:
                        if elem.is_pseudo:
                            res += "_"
                        else:
                            res += "."
            res += "\n"
        return res


def getRegionsFromFields(m: AugmentedMap) -> list[Region]:
    res: list[Region] = []

    for row in m.fields:
        for elem in row:
            if not elem.is_main_loop:
                neighbors = m.getNeighbors(elem)
                found_regions: list[Region] = []

                for region in res:
                    for n in neighbors:
                        if n in region:
                            region.append(elem)
                            found_regions.append(region)
                            break

                if found_regions == []:
                    res.append([elem])
                else:
                    merged_region: Region = []
                    for region in found_regions:
                        merged_region += region
                        res.remove(region)
                    res.append(merged_region)
    return res


def getRegionBorderFields(m: AugmentedMap, region: Region) -> list[AugmentedField]:
    res: list[AugmentedField] = []
    for field in region:
        neighbors = m.getNeighbors(field)
        if len(neighbors) != 4:
            # field is at map border, so must be border itself
            res.append(field)
        else:
            for neighbor in neighbors:
                if neighbor not in region:
                    res.append(field)
                    break
    return res


def isSurroundedByLoop(m: AugmentedMap, region: Region) -> bool:
    borders = getRegionBorderFields(m, region)
    for border in borders:
        border_neighbors = m.getNeighbors(border)
        if len(border_neighbors) != 4:
            return False
        neighbor_loops = [x for x in border_neighbors if x.is_main_loop]
        if len(neighbor_loops) == 0:
            return False

    return True


if __name__ == "__main__":
    example_txt = """
.....
.S-7.
.|.|.
.L-J.
.....
"""
    lines = [line.strip() for line in example_txt.split("\n") if line.strip() != ""]
    example = readMap(lines)
    loop = createLoop(example)
    assignDistances(loop)
    unwrapped = unwrapLoop(loop)
    assert max([x.distance for x in unwrapped]) == 4

    other_example_txt = """
...........
.S-------7.
.|F-----7|.
.||.....||.
.||.....||.
.|L-7.F-J|.
.|..|.|..|.
.L--J.L--J.
...........
"""
    other_lines = [line.strip() for line in other_example_txt.split("\n") if line.strip() != ""]
    other_example = readMap(other_lines)
    loop = createLoop(other_example)
    assignDistances(loop)
    unwrapped = unwrapLoop(loop)

    augmented = AugmentedMap(other_example)
    nice = NiceMap(augmented)
    print(str(nice))

    regions = getRegionsFromFields(augmented)
    for r in regions:
        print(str(NiceRegion(augmented, r)))

    surrounded_regions = [x for x in regions if isSurroundedByLoop(augmented, x)]
    filtered_surrounded_regions = [[x for x in region if not x.is_pseudo] for region in surrounded_regions]
    num_surrounded_fields = sum([len(x) for x in filtered_surrounded_regions])
    assert num_surrounded_fields == 4


    example_txt_2 = """
FF7FSF7F7F7F7F7F---7
L|LJ||||||||||||F--J
FL-7LJLJ||||||LJL-77
F--JF--7||LJLJ7F7FJ-
L---JF-JLJ.||-FJLJJ7
|F|F-JF---7F7-L7L|7|
|FFJF7L7F-JF7|JL---7
7-L-JL7||F7|L7F-7F7|
L.L7LFJ|||||FJL7||LJ
L7JLJL-JLJLJL--JLJ.L
"""
    lines = [line.strip() for line in example_txt_2.split("\n") if line.strip() != ""]
    example_2 = readMap(lines)
    loop = createLoop(example_2)
    assignDistances(loop)
    unwrapped = unwrapLoop(loop)

    augmented = AugmentedMap(example_2)
    print(str(augmented))

    nice = NiceMap(augmented)
    print(str(nice))

    regions = getRegionsFromFields(augmented)
    surrounded_regions = [x for x in regions if isSurroundedByLoop(augmented, x)]
    filtered_surrounded_regions = [[x for x in region if not x.is_pseudo] for region in surrounded_regions]
    num_surrounded_fields = sum([len(x) for x in filtered_surrounded_regions])
    assert num_surrounded_fields == 10
