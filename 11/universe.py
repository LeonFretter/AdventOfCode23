from dataclasses import dataclass


@dataclass
class Vec2:
    x: int
    y: int

    def __add__(self, other: "Vec2"):
        return Vec2(self.x + other.x, self.y + other.y)


def isEmptyRow(lines: list[str], row: int) -> bool:
    return len([x for x in lines[row] if x == '#']) == 0


def isEmptyColumn(lines: list[str], column: int) -> bool:
    return len([x for x in lines if x[column] == '#']) == 0


def createExpansionMap(lines: list[str], expansion: int) -> list[list[Vec2]]:
    res: list[list[Vec2]] = []
    for row_idx, line in enumerate(lines):
        res.append([Vec2(1, 1) for _ in range(len(line))])

    for row_idx, line in enumerate(lines):
        if isEmptyRow(lines, row_idx):
            for col_idx in range(len(line)):
                res[row_idx][col_idx].y = expansion

    for col_idx in range(len(lines[0])):
        if isEmptyColumn(lines, col_idx):
            for row_idx in range(len(lines)):
                res[row_idx][col_idx].x = expansion

    return res


def createPositionMap(lines: list[str], expansion: int) -> list[list[Vec2]]:
    expansions = createExpansionMap(lines, expansion)
    it = Vec2(0, 0)
    for row in expansions:
        it.x = 0
        next_y = it.y + row[0].y
        for cell in row:
            next_x = it.x + cell.x
            cell.x = it.x
            cell.y = it.y
            it.x = next_x
        it.y = next_y
    return expansions


@dataclass
class Galaxy:
    position: Vec2

    def countSteps(self, other: "Galaxy") -> int:
        return abs(self.position.x - other.position.x) + abs(self.position.y - other.position.y)


def findGalaxies(universe: list[str], positions: list[list[Vec2]]) -> list[Galaxy]:
    res: list[Galaxy] = []
    for y, row in enumerate(universe):
        for x, cell in enumerate(row):
            if cell == '#':
                pos = positions[y][x]
                res.append(Galaxy(pos))
    return res


def buildPairs(galaxies: list[Galaxy]) -> list[tuple[Galaxy, Galaxy]]:
    res: list[tuple[Galaxy, Galaxy]] = []
    for i, galaxy in enumerate(galaxies):
        for j in range(i + 1, len(galaxies)):
            res.append((galaxy, galaxies[j]))
    return res


def countSteps(galaxies: list[Galaxy]) -> int:
    steps = 0
    for i, galaxy in enumerate(galaxies):
        for j in range(i + 1, len(galaxies)):
            steps += galaxy.countSteps(galaxies[j])
    return steps


if __name__ == "__main__":
    example_txt1 = """
...#......
.......#..
#.........
..........
......#...
.#........
.........#
..........
.......#..
#...#.....
"""
    lines = [x for x in example_txt1.split('\n') if x != '']
    positions = createPositionMap(lines, 2)

    galaxies = findGalaxies(lines, positions)
    assert len(galaxies) == 9
    pairs = buildPairs(galaxies)
    assert len(pairs) == 36
    num_steps = countSteps(galaxies)
    assert num_steps == 374

    positions2 = createPositionMap(lines, 10)
    galaxies2 = findGalaxies(lines, positions2)
    assert len(galaxies2) == 9
    num_steps = countSteps(galaxies2)
    assert num_steps == 1030

    positions3 = createPositionMap(lines, 100)
    galaxies3 = findGalaxies(lines, positions3)
    assert len(galaxies3) == 9
    num_steps = countSteps(galaxies3)
    assert num_steps == 8410
