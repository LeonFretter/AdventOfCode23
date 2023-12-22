from dataclasses import dataclass


@dataclass
class Vec2:
    x: int
    y: int

    def __hash__(self) -> int:
        return hash((self.x, self.y))


@dataclass
class Vec3:
    x: int
    y: int
    z: int

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.z))


@dataclass
class Brick:
    name: str
    start: Vec3
    end: Vec3

    def coords(self) -> list[Vec3]:
        coords = []
        for x in range(self.start.x, self.end.x + 1):
            for y in range(self.start.y, self.end.y + 1):
                for z in range(self.start.z, self.end.z + 1):
                    coords.append(Vec3(x, y, z))
        return coords

    def __eq__(self, other: "Brick") -> bool:
        return self.name == other.name

    def __hash__(self) -> int:
        return hash((self.name, self.start, self.end))


def readBrick(line: str, i: int) -> Brick:
    first, second = line.split("~")
    first_coords = first.split(",")
    second_coords = second.split(",")
    start = Vec3(int(first_coords[0]), int(first_coords[1]), int(first_coords[2]))
    end = Vec3(int(second_coords[0]), int(second_coords[1]), int(second_coords[2]))
    name = str(i)
    return Brick(name, start, end)


def readBricks(lines: list[str]) -> list[Brick]:
    return [readBrick(line, i) for i, line in enumerate(lines)]


@dataclass
class Tile:
    pos: Vec2
    occupied: Brick | None = None


@dataclass
class Layer:
    tiles: list[list[Tile]]
    z: int

    def __str__(self) -> str:
        res = ""
        for row in self.tiles:
            row_str = ""
            for tile in row:
                if tile.occupied is None:
                    row_str += "."
                else:
                    row_str += tile.occupied.name
            res += row_str + "\n"
        return res


@dataclass
class BrickMap:
    def __init__(self, bricks: list[Brick]):
        self.bricks = bricks
        self.bricks.sort(key=lambda brick: brick.start.z)
        self.w = self._maxX() + 1
        self.h = self._maxY() + 1
        self.d = self._maxZ() + 1

        self.layers = [self.createLayer(z) for z in range(self.d)]

    def _maxX(self) -> int:
        return max([brick.end.x for brick in self.bricks])

    def _maxY(self) -> int:
        return max([brick.end.y for brick in self.bricks])

    def _maxZ(self) -> int:
        return max([brick.end.z for brick in self.bricks])

    def bricksAtLayer(self, z: int, limit_to_starting=False) -> list[Brick]:
        if limit_to_starting:
            return [brick for brick in self.bricks if brick.start.z == z]
        else:
            return [brick for brick in self.bricks if brick.start.z <= z <= brick.end.z]

    def createLayer(self, z: int) -> Layer:
        layer = []
        for y in range(self.h):
            row = []
            for x in range(self.w):
                row.append(Tile(Vec2(x, y)))
            layer.append(row)

        layer_bricks = self.bricksAtLayer(z)
        for brick in layer_bricks:
            for coord in brick.coords():
                if coord.z == z:
                    layer[coord.y][coord.x].occupied = brick

        return Layer(layer, z)

    def updateLayer(self, z: int) -> bool:
        if z == 0:
            return False
        else:
            changed = False
            bricks = self.bricksAtLayer(z, limit_to_starting=True)
            for brick in bricks:
                if self.supportGiven(brick) == []:
                    current_coords = brick.coords()
                    changed = True
                    brick.start.z -= 1
                    brick.end.z -= 1
                    for coord in current_coords:
                        self.layers[coord.z].tiles[coord.y][coord.x].occupied = None
                    new_coords = brick.coords()
                    for coord in new_coords:
                        self.layers[coord.z].tiles[coord.y][coord.x].occupied = brick
            return changed

    def update(self) -> bool:
        changed = False
        for z in range(self.d):
            if self.updateLayer(z):
                changed = True
        return changed

    def run(self) -> None:
        i = 0
        while self.update():
            if i % 10 == 0:
                print(f"i: {i}")
            i += 1

    def supportGiven(self, brick: Brick) -> list[Brick]:
        """
        Returns a list of bricks that give support to the given brick.
        """
        res = []
        if brick.start.z == 0:
            return []
        elif brick.start.z != brick.end.z:
            layer_below = self.layers[brick.start.z - 1]
            tile_below = layer_below.tiles[brick.start.y][brick.start.x]
            if tile_below.occupied is not None and tile_below.occupied != brick:
                res.append(tile_below.occupied)
        else:
            layer_below = self.layers[brick.start.z - 1]
            for coord in brick.coords():
                tile_below = layer_below.tiles[coord.y][coord.x]
                if tile_below.occupied is not None and tile_below.occupied != brick:
                    res.append(tile_below.occupied)
        assert brick not in res
        return list(set(res))

    def supportedBy(self, brick: Brick) -> list[Brick]:
        """
        Returns a list of bricks that are supported by the given brick.
        """
        res = []
        if brick.end.z == self.d - 1:
            return []
        elif brick.start.z != brick.end.z:
            layer_above = self.layers[brick.end.z + 1]
            tile_above = layer_above.tiles[brick.end.y][brick.end.x]
            if tile_above.occupied is not None and tile_above.occupied != brick:
                res.append(tile_above.occupied)
        else:
            layer_above = self.layers[brick.end.z + 1]
            for coord in brick.coords():
                tile_above = layer_above.tiles[coord.y][coord.x]
                if tile_above.occupied is not None and tile_above.occupied != brick:
                    res.append(tile_above.occupied)
        assert brick not in res
        return list(set(res))

    def canDisintegrate(self, brick: Brick) -> bool:
        brick_supports = self.supportedBy(brick)
        for supported in brick_supports:
            supported_by = self.supportGiven(supported)
            if len(supported_by) == 1:
                return False
        return True

    def countDisintegratable(self) -> int:
        res = 0
        for brick in self.bricks:
            if self.canDisintegrate(brick):
                res += 1
        return res


if __name__ == "__main__":
    txt: str = """\
1,0,1~1,2,1
0,0,2~2,0,2
0,2,3~2,2,3
0,0,4~0,2,4
2,0,5~2,2,5
0,1,6~2,1,6
1,1,8~1,1,9\
"""
    lines: list[str] = txt.split("\n")
    bricks = readBricks(lines)
    brick_map = BrickMap(bricks)
    brick_map.run()
    disintegratable = brick_map.countDisintegratable()
    assert disintegratable == 5

    example_brick = Brick("example", Vec3(0, 0, 0), Vec3(0, 0, 2))
    coords = example_brick.coords()
    assert coords == [Vec3(0, 0, 0), Vec3(0, 0, 1), Vec3(0, 0, 2)]

    example_brick2 = Brick("example2", Vec3(0, 0, 3), Vec3(0, 2, 3))

    example_map = BrickMap([example_brick, example_brick2])
    assert example_map.canDisintegrate(example_brick2)
    assert not example_map.canDisintegrate(example_brick)
    assert example_map.countDisintegratable() == 1
