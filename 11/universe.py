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


def createExpandedUniverse(lines: list[str]) -> list[str]:
    expanded: list[str] = []
    for row_idx, line in enumerate(lines):
        expanded.append(line)
        if isEmptyRow(lines, row_idx):
            expanded.append(line)

    expanded_col_idx = 0
    for col_idx in range(len(lines[0])):
        if isEmptyColumn(lines, col_idx):
            for row_idx, line in enumerate(expanded):
                expanded[row_idx] = line[:expanded_col_idx] + '.' + line[expanded_col_idx:]
            expanded_col_idx += 1
        expanded_col_idx += 1

    return expanded





@dataclass
class Galaxy:
    position: Vec2

    def countSteps(self, other: "Galaxy") -> int:
        return abs(self.position.x - other.position.x) + abs(self.position.y - other.position.y)


def findGalaxies(universe: list[str]) -> list[Galaxy]:
    res: list[Galaxy] = []
    for y, row in enumerate(universe):
        for x, cell in enumerate(row):
            if cell == '#':
                res.append(Galaxy(Vec2(x, y)))
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
    universe = createExpandedUniverse(lines)
    for l in universe:
        print(l)

    galaxies = findGalaxies(universe)
    assert len(galaxies) == 9
    pairs = buildPairs(galaxies)
    assert len(pairs) == 36
    num_steps = countSteps(galaxies)
    assert num_steps == 374
