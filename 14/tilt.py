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
        self.columns: list[list[Object]] = []
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
        for x in range(self.w):
            self.columns.append([])
            for y in range(self.h):
                obj = next((o for o in self.rows[y] if o.position.x == x), None)
                if obj is not None:
                    self.columns[x].append(obj)

    def copy(self) -> "Board":
        stringified = str(self)
        lines = stringified.split("\n")
        return Board(lines)

    def getFurthestFreePosNorth(self, obj: Object) -> Vec2:
        row_idx = self.columns[obj.position.x].index(obj)
        if row_idx == 0:
            return Vec2(obj.position.x, 0)
        else:
            obj_north = self.columns[obj.position.x][row_idx - 1]
            return Vec2(obj.position.x, obj_north.position.y + 1)

    def getFurthestFreePosSouth(self, obj: Object) -> Vec2:
        row_idx = self.columns[obj.position.x].index(obj)
        if row_idx == len(self.columns[obj.position.x]) - 1:
            return Vec2(obj.position.x, self.h - 1)
        else:
            obj_south = self.columns[obj.position.x][row_idx + 1]
            return Vec2(obj.position.x, obj_south.position.y - 1)

    def getFurthestFreePosWest(self, obj: Object) -> Vec2:
        col_idx = self.rows[obj.position.y].index(obj)
        if col_idx == 0:
            return Vec2(0, obj.position.y)
        else:
            obj_west = self.rows[obj.position.y][col_idx - 1]
            return Vec2(obj_west.position.x + 1, obj.position.y)

    def getFurthestFreePosEast(self, obj: Object) -> Vec2:
        col_idx = self.rows[obj.position.y].index(obj)
        if col_idx == len(self.rows[obj.position.y]) - 1:
            return Vec2(self.w - 1, obj.position.y)
        else:
            obj_east = self.rows[obj.position.y][col_idx + 1]
            return Vec2(obj_east.position.x - 1, obj.position.y)

    def move(self, obj: Object, new_pos: Vec2) -> None:
        self.rows[obj.position.y].remove(obj)
        self.columns[obj.position.x].remove(obj)
        obj.position = new_pos
        new_idx_in_row = next(
            (i for i, o in enumerate(self.rows[new_pos.y]) if o.position.x > new_pos.x),
            len(self.rows[new_pos.y]),
        )
        new_idx_in_col = next(
            (i for i, o in enumerate(self.columns[new_pos.x]) if o.position.y > new_pos.y),
            len(self.columns[new_pos.x]),
        )
        self.rows[new_pos.y].insert(new_idx_in_row, obj)
        self.columns[new_pos.x].insert(new_idx_in_col, obj)

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

    def __eq__(self, other: "Board") -> bool:
        return str(self) == str(other)


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

    board1 = board.copy()
    board2 = board.copy()
    assert board1 == board2
    board1.rollSouth()
    board1.rollNorth()
    assert board1 == board2
