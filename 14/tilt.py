from enum import Enum
from dataclasses import dataclass


class ObjectType(Enum):
    FIXED_ROCK = 1
    MOVABLE_ROCK = 2


class Direction(Enum):
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4


@dataclass
class Vec2:
    x: int
    y: int

    def __eq__(self, other: "Vec2") -> bool:
        return self.x == other.x and self.y == other.y


@dataclass
class Object:
    object_type: ObjectType
    position: Vec2


class Board:
    def __init__(self, lines: list[str]):
        self.w = len(lines[0])
        self.h = len(lines)
        self.rows: list[list[Object]] = []
        self.objects: list[Object] = []
        self.movable: list[Object] = []

        for y, row in enumerate(lines):
            self.rows.append([])
            for x, c in enumerate(row):
                if c == "O":
                    obj = Object(ObjectType.MOVABLE_ROCK, Vec2(x, y))
                    self.rows[y].append(obj)
                    self.objects.append(obj)
                    self.movable.append(obj)
                elif c == "#":
                    obj = Object(ObjectType.FIXED_ROCK, Vec2(x, y))
                    self.rows[y].append(obj)
                else:
                    continue

    def getFurthestFreePosNorth(self, obj: Object) -> Vec2 | None:
        pos = obj.position
        free_pos = None
        for y in range(pos.y - 1, -1, -1):
            found_solid = False
            row = self.rows[y]
            for o in row:
                if o.position.x > pos.x:
                    break
                if o.position.x == pos.x:
                    found_solid = True
                    break
            if found_solid:
                break
            else:
                free_pos = Vec2(pos.x, y)
        return free_pos

    def getFurthestFreePosSouth(self, obj: Object) -> Vec2 | None:
        pos = obj.position
        free_pos = None
        for y in range(pos.y + 1, len(self.rows)):
            found_solid = False
            for o in self.rows[y]:
                if o.position.x > pos.x:
                    break
                if o.position.x == pos.x:
                    found_solid = True
            if found_solid:
                break
            else:
                free_pos = Vec2(pos.x, y)
        return free_pos

    def getFurthestFreePosWest(self, obj: Object) -> Vec2 | None:
        col_idx = self.rows[obj.position.y].index(obj)
        if col_idx == 0:
            return Vec2(0, obj.position.y)
        else:
            obj_west = self.rows[obj.position.y][col_idx - 1]
            return Vec2(obj_west.position.x + 1, obj.position.y)

    def getFurthestFreePosEast(self, obj: Object) -> Vec2 | None:
        col_idx = self.rows[obj.position.y].index(obj)
        if col_idx == len(self.rows[obj.position.y]) - 1:
            return Vec2(self.w - 1, obj.position.y)
        else:
            obj_east = self.rows[obj.position.y][col_idx + 1]
            return Vec2(obj_east.position.x - 1, obj.position.y)

    def move(self, obj: Object, new_pos: Vec2) -> None:
        self.rows[obj.position.y].remove(obj)
        obj.position = new_pos
        self.rows[new_pos.y].append(obj)
        self.rows[new_pos.y].sort(key=lambda o: o.position.x)

    def rollNorth(self) -> None:
        while True:
            moved = []
            for obj in self.movable:
                furthest_free_pos = self.getFurthestFreePosNorth(obj)
                if furthest_free_pos is not None and furthest_free_pos != obj.position:
                    moved.append(obj)
                    self.move(obj, furthest_free_pos)
            if len(moved) == 0:
                break

    def rollSouth(self) -> None:
        while True:
            moved = []
            for obj in self.movable:
                furthest_free_pos = self.getFurthestFreePosSouth(obj)
                if furthest_free_pos is not None and furthest_free_pos != obj.position:
                    moved.append(obj)
                    self.move(obj, furthest_free_pos)
            if len(moved) == 0:
                break

    def rollWest(self) -> None:
        while True:
            moved = []
            for obj in self.movable:
                furthest_free_pos = self.getFurthestFreePosWest(obj)
                if furthest_free_pos is not None and furthest_free_pos != obj.position:
                    moved.append(obj)
                    self.move(obj, furthest_free_pos)
            if len(moved) == 0:
                break

    def rollEast(self) -> None:
        while True:
            moved = []
            for obj in self.movable:
                furthest_free_pos = self.getFurthestFreePosEast(obj)
                if furthest_free_pos is not None and furthest_free_pos != obj.position:
                    moved.append(obj)
                    self.move(obj, furthest_free_pos)
            if len(moved) == 0:
                break

    def roll(self, direction: Direction) -> None:
        match direction:
            case Direction.NORTH:
                self.rollNorth()
            case Direction.SOUTH:
                self.rollSouth()
            case Direction.WEST:
                self.rollWest()
            case Direction.EAST:
                self.rollEast()

    def spinCycle(self) -> None:
        self.roll(Direction.NORTH)
        self.roll(Direction.WEST)
        self.roll(Direction.SOUTH)
        self.roll(Direction.EAST)

    def getWeight(self) -> int:
        weight = 0
        for obj in self.movable:
            weight += len(self.rows) - obj.position.y
        return weight

    def __str__(self) -> str:
        lines: list[str] = []
        new_line: str = ""
        for y, row in enumerate(self.rows):
            pos = Vec2(0, y)
            for x, obj in enumerate(row):
                for fill_x in range(pos.x, obj.position.x):
                    new_line += "."
                if obj.object_type == ObjectType.FIXED_ROCK:
                    new_line += "#"
                else:
                    new_line += "O"
                pos = Vec2(obj.position.x + 1, y)
            for _ in range(pos.x, self.w):
                new_line += "."
            lines.append(new_line)
            new_line = ""
        return "\n".join(lines)


if __name__ == "__main__":
    txt = str("""\
O....#....
O.OO#....#
.....##...
OO.#O....O
.O.....O#.
O.#..O.#.#
..O..#O..O
.......O..
#....###..
#OO..#....\
""")
    lines = txt.strip().split("\n")
    board = Board(lines)
    board.rollNorth()
    w = board.getWeight()
    assert w == 136

    new_board = Board(lines)
    new_board.spinCycle()
    expected_txt = """\
.....#....
....#...O#
...OO##...
.OO#......
.....OOO#.
.O#...O#.#
....O#....
......OOOO
#...O###..
#..OO#....\
"""
    result_txt = str(new_board)
    print("\n\n")
    print(result_txt)
    assert result_txt == expected_txt
