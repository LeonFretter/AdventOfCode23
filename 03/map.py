from dataclasses import dataclass


@dataclass
class Char:
    x: int
    y: int
    char: str


@dataclass
class Word:
    chars: list[Char]

    def getString(self) -> str:
        return "".join([c.char for c in self.chars])

    def getNumber(self) -> int:
        return int(self.getString())


class Map:
    def __init__(self, lines: list[str]):
        self.width = len(lines[0])
        self.height = len(lines)
        self.chars: list[list[Char]] = []
        for line in lines:
            y = len(self.chars)
            self.chars.append([])
            for c in line:
                x = len(self.chars[-1])
                self.chars[-1].append(Char(x, y, c))

    def getChar(self, x: int, y: int) -> Char:
        return self.chars[y][x]

    def getNeighbors(self, char: Char) -> list[Char]:
        x = char.x
        y = char.y
        neighbors: list[Char] = []
        minx = max(0, x - 1)
        miny = max(0, y - 1)
        maxx = min(self.width, x + 2)
        maxy = min(self.height, y + 2)
        for xi in range(minx, maxx):
            for yi in range(miny, maxy):
                if xi == x and yi == y:
                    continue
                neighbors.append(self.getChar(xi, yi))
        return neighbors

    def getNumbers(self) -> list[Word]:
        numbers: list[Word] = []
        for y in range(self.height):
            current_word: list[Char] = []
            for x in range(self.width):
                c = self.getChar(x, y)
                if c.char.isdigit():
                    current_word.append(c)

                if len(current_word) > 0 and (not c.char.isdigit() or x == self.width - 1):
                    numbers.append(Word(current_word))
                    current_word = []

        return numbers

    def isAdjacentToSymbol(self, word: Word) -> bool:
        for c in word.chars:
            neighbors = self.getNeighbors(c)
            for n in neighbors:
                c = n.char
                if not c.isdigit() and not c.isalpha() and c != '.':
                    return True
        return False

    def getNumbersAdjacentToSymbol(self) -> list[Word]:
        numbers = self.getNumbers()
        return [n for n in numbers if self.isAdjacentToSymbol(n)]


if __name__ == "__main__":
    lines1 = [
        ".12",
        "..-",
        "...",
        "345"
    ]
    map1 = Map(lines1)
    assert map1.width == 3
    assert map1.height == 4
    c1 = map1.getChar(0, 0)
    assert c1.char == '.'
    assert c1.x == 0
    assert c1.y == 0

    neighbors11 = map1.getNeighbors(map1.getChar(0, 0))
    assert len(neighbors11) == 3
    assert Char(1, 0, '1') in neighbors11
    assert Char(0, 1, '.') in neighbors11
    assert Char(1, 1, '.') in neighbors11

    neighbors12 = map1.getNeighbors(map1.getChar(2, 0))
    assert len(neighbors12) == 3
    assert Char(1, 0, '1') in neighbors12
    assert Char(1, 1, '.') in neighbors12
    assert Char(2, 1, '-') in neighbors12

    numbers1 = map1.getNumbers()
    assert len(numbers1) == 2
    assert numbers1[0].getNumber() == 12
    assert numbers1[1].getNumber() == 345

    res1 = map1.getNumbersAdjacentToSymbol()
    assert len(res1) == 1
    assert res1[0].getNumber() == 12

    lines2 = [
        "467..114..",
        "...*......",
        "..35..633.",
        "......#...",
        "617*......",
        ".....+.58.",
        "..592.....",
        "......755.",
        "...$.*....",
        ".664.598..",
    ]
    map2 = Map(lines2)
    nums = [x.getNumber() for x in map2.getNumbersAdjacentToSymbol()]
    res = sum(nums)
    assert res == 4361
