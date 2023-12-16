from dataclasses import dataclass, field
from enum import Enum


class TileType(Enum):
    EMPTY = 0
    VERTICAL = 1
    HORIZONTAL = 2
    LEFT_RIGHT = 3
    RIGHT_LEFT = 4


@dataclass
class Vec2:
    x: int
    y: int

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __hash__(self) -> int:
        return self.y * 10000 + self.x

    @staticmethod
    def zero() -> "Vec2":
        return Vec2(0, 0)

    @staticmethod
    def up() -> "Vec2":
        return Vec2(0, -1)

    @staticmethod
    def down() -> "Vec2":
        return Vec2(0, 1)

    @staticmethod
    def left() -> "Vec2":
        return Vec2(-1, 0)

    @staticmethod
    def right() -> "Vec2":
        return Vec2(1, 0)


@dataclass
class Tile:
    tile_type: TileType
    pos: Vec2
    beam_directions: "list[Vec2]" = field(default_factory=list)

    @property
    def energized(self) -> bool:
        return len(self.beam_directions) > 0


@dataclass
class Map:
    tiles: list[list[Tile]]

    def getTile(self, pos: Vec2) -> Tile | None:
        if pos.x < 0 or pos.x >= len(self.tiles[0]) or pos.y < 0 or pos.y >= len(self.tiles):
            return None
        return self.tiles[pos.y][pos.x]

    def __str__(self) -> str:
        res = ""
        for row in self.tiles:
            for tile in row:
                if tile.energized:
                    res += "#"
                else:
                    match tile.tile_type:
                        case TileType.EMPTY:
                            res += "."
                        case TileType.VERTICAL:
                            res += "|"
                        case TileType.HORIZONTAL:
                            res += "-"
                        case TileType.LEFT_RIGHT:
                            res += "\\"
                        case TileType.RIGHT_LEFT:
                            res += "/"
            res += "\n"
        return res


@dataclass
class Beam:
    positions: list[tuple[Vec2, Vec2]]

    @property
    def direction(self) -> Vec2:
        return self.positions[-1][1]

    @property
    def position(self) -> Vec2:
        return self.positions[-1][0]

    def nextSections(self, map: Map) -> list[tuple[Vec2, Vec2]]:
        next_tile = map.getTile(self.position + self.direction)
        if next_tile is None:
            return []
        next_sections: list[tuple[Vec2, Vec2]] = []

        match next_tile.tile_type:
            case TileType.EMPTY:
                next_sections = [(next_tile.pos, self.direction)]
            case TileType.VERTICAL:
                if self.direction == Vec2.up() or self.direction == Vec2.down():
                    next_sections = [(next_tile.pos, self.direction)]
                else:
                    next_sections = [(next_tile.pos, Vec2.up()), (next_tile.pos, Vec2.down())]
            case TileType.HORIZONTAL:
                if self.direction == Vec2.left() or self.direction == Vec2.right():
                    next_sections = [(next_tile.pos, self.direction)]
                else:
                    next_sections = [(next_tile.pos, Vec2.left()), (next_tile.pos, Vec2.right())]
            case TileType.LEFT_RIGHT:
                transformations = {
                    Vec2.up(): Vec2.left(),
                    Vec2.down(): Vec2.right(),
                    Vec2.left(): Vec2.up(),
                    Vec2.right(): Vec2.down()
                }
                new_direction = transformations[self.direction]
                next_sections = [(next_tile.pos, new_direction)]
            case TileType.RIGHT_LEFT:
                transformations = {
                    Vec2.up(): Vec2.right(),
                    Vec2.down(): Vec2.left(),
                    Vec2.left(): Vec2.down(),
                    Vec2.right(): Vec2.up()
                }
                new_direction = transformations[self.direction]
                next_sections = [(next_tile.pos, new_direction)]

        res: list[tuple[Vec2, Vec2]] = []
        for next_section in next_sections:
            direction = next_section[1]
            if direction not in next_tile.beam_directions:
                res.append(next_section)

        return res

    def grow(self, map: Map) -> "list[Beam]":
        next_sections = self.nextSections(map)
        if len(next_sections) == 0:
            return [Beam(self.positions)]
        else:
            res: list[Beam] = []
            for next_section in next_sections:
                next_tile = map.getTile(next_section[0])
                next_tile.beam_directions.append(next_section[1])

                new_positions = self.positions.copy()
                new_positions.append(next_section)
                res.append(Beam(new_positions))
            return res

    def __eq__(self, other: "Beam") -> bool:
        return self.positions == other.positions


def readMap(txt: str) -> Map:
    tiles = []
    for y, line in enumerate(txt.splitlines()):
        tiles.append([])
        for x, char in enumerate(line):
            match char:
                case ".":
                    tiles[y].append(Tile(TileType.EMPTY, Vec2(x, y)))
                case "|":
                    tiles[y].append(Tile(TileType.VERTICAL, Vec2(x, y)))
                case "-":
                    tiles[y].append(Tile(TileType.HORIZONTAL, Vec2(x, y)))
                case "/":
                    tiles[y].append(Tile(TileType.RIGHT_LEFT, Vec2(x, y)))
                case "\\":
                    tiles[y].append(Tile(TileType.LEFT_RIGHT, Vec2(x, y)))
                case _:
                    raise ValueError(f"Unknown tile type: {char}")
    return Map(tiles)


def createBeams(m: Map, do_print=False) -> list[Beam]:
    beams = [
        Beam([(Vec2.zero(), Vec2.right())]),
    ]
    m.getTile(Vec2.zero()).beam_directions.append(Vec2.right())
    while True:
        next_beams = []
        changed = False
        for beam in beams:
            new_beams = beam.grow(m)
            if do_print:
                print(m)
                print("\n")
            if len(new_beams) > 1 or new_beams[0] != beam:
                changed = True
            next_beams += new_beams
        if not changed:
            break
        beams = next_beams

    return beams


def countEnergized(m: Map) -> int:
    count = 0
    for row in m.tiles:
        for tile in row:
            if tile.energized:
                count += 1
    return count


if __name__ == "__main__":
    txt = """\
.|...\\....
|.-.\\.....
.....|-...
........|.
..........
.........\\
..../.\\\\..
.-.-/..|..
.|....-|.\\
..//.|....\
"""
    m = readMap(txt)
    beams = createBeams(m, True)
    print(m)
    count = countEnergized(m)
    assert count == 46
