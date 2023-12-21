from dataclasses import dataclass
from enum import Enum
import sys


class TileType(Enum):
    EMPTY = "."
    WALL = "#"
    START = "S"


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

    def __hash__(self) -> int:
        return hash((self.x, self.y))


@dataclass
class Tile:
    tile_type: TileType
    pos: Vec2

    def __eq__(self, other: "Tile") -> bool:
        return self.pos == other.pos

    def __hash__(self) -> int:
        return hash(self.pos)


@dataclass
class Map[T]:
    tiles: list[list[T]]

    def tile(self, pos: Vec2) -> T:
        return self.tiles[pos.y][pos.x]

    def neighbors(self, pos: Vec2) -> list[Tile]:
        """
            Doesn't include diagonals
        """
        min_x = max(pos.x - 1, 0)
        max_x = min(pos.x + 1, len(self.tiles[0]) - 1)
        min_y = max(pos.y - 1, 0)
        max_y = min(pos.y + 1, len(self.tiles) - 1)

        neighbors = []
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if x == pos.x and y == pos.y:
                    continue
                if x == pos.x or y == pos.y:
                    neighbors.append(self.tiles[y][x])
        return neighbors

    def nonWallNeighbors(self, pos: Vec2) -> list[Tile]:
        return [n for n in self.neighbors(pos) if n.tile_type != TileType.WALL]

    def findByType(self: "Map[Tile]", tile_type: TileType) -> Tile:
        for row in self.tiles:
            for tile in row:
                if tile.tile_type == tile_type:
                    return tile
        raise ValueError(f"Could not find tile of type {tile_type}")

    def findStart(self: "Map[Tile]") -> Tile:
        return self.findByType(TileType.START)

    def distanceMap(self: "Map[Tile]", start: Vec2, max_dist: int = sys.maxsize) -> "Map[int]":
        distances = [[sys.maxsize for _ in row] for row in self.tiles]
        distances[start.y][start.x] = 0
        stack = [start]
        while stack:
            pos = stack.pop()
            for neighbor in self.neighbors(pos):
                if isinstance(neighbor, Tile):
                    if neighbor.tile_type == TileType.WALL:
                        continue
                current_dist = distances[pos.y][pos.x]
                new_dist = current_dist + 1
                if new_dist < distances[neighbor.pos.y][neighbor.pos.x]:
                    distances[neighbor.pos.y][neighbor.pos.x] = new_dist
                    if new_dist < max_dist:
                        stack.append(neighbor.pos)
        return Map(distances)

    def countFiniteDist(self: "Map[int]") -> int:
        count = 0
        for row in self.tiles:
            for dist in row:
                if dist != sys.maxsize:
                    count += 1
        return count

    def reachable(self: "Map[Tile]", start: Tile, steps: int) -> "set[Tile]":
        elems: set[Tile] = {start}
        for _ in range(steps):
            new_elems = set()
            for elem in elems:
                new_elems.update(new_elems, self.nonWallNeighbors(elem.pos))
            elems = new_elems
        return new_elems


type TileMap = Map[Tile]


def readMap(txt: str) -> TileMap:
    lines = txt.splitlines()
    tiles = []
    for y, line in enumerate(lines):
        row = []
        for x, char in enumerate(line):
            tile_type = TileType(char)
            pos = Vec2(x, y)
            tile = Tile(tile_type, pos)
            row.append(tile)
        tiles.append(row)
    return Map(tiles)


if __name__ == "__main__":
    txt = """\
...........
.....###.#.
.###.##..#.
..#.#...#..
....#.#....
.##..S####.
.##..#...#.
.......##..
.##.#.####.
.##..##.##.
...........\
"""

    m = readMap(txt)
    start = m.findStart()
    reachable = m.reachable(start, 6)
    num_reachable = len(reachable)
    print(f"Number of reachable tiles: {num_reachable}")
    assert num_reachable == 16
