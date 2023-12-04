from dataclasses import dataclass
from enum import Enum

red = 12
green = 13
blue = 14


@dataclass
class Game:
    reds: list[int]
    greens: list[int]
    blues: list[int]
    idx: int


class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


def getColor(s : str) -> Color:
    match s:
        case "red":
            return Color.RED
        case "green":
            return Color.GREEN
        case "blue":
            return Color.BLUE
        case _:
            raise Exception("Invalid color")


def readGame(line: str) -> Game:
    header, colorTxt = line.split(":")
    idx = int(header.split(" ")[1])
    colorTxt = colorTxt.replace(";", ",")
    colors = colorTxt.split(",")
    colorPairs: list[tuple[Color, int]] = []
    for c in colors:
        num, color = c.strip().split(" ")
        colorPairs.append((getColor(color), int(num)))

    reds = [n for c, n in colorPairs if c == Color.RED]
    greens = [n for c, n in colorPairs if c == Color.GREEN]
    blues = [n for c, n in colorPairs if c == Color.BLUE]
    return Game(reds, greens, blues, idx)


def isPossible(game: Game) -> bool:
    fr = list(filter(lambda x: x > red, game.reds))
    fg = list(filter(lambda x: x > green, game.greens))
    fb = list(filter(lambda x: x > blue, game.blues))

    return len(fr) == 0 and len(fg) == 0 and len(fb) == 0


def possibleIndices(games: list[Game]) -> list[int]:
    return [g.idx for g in games if isPossible(g)]


def possibleIndicesSum(games: list[Game]) -> int:
    return sum(possibleIndices(games))


def findPower(game: Game) -> int:
    return max(game.reds) * max(game.greens) * max(game.blues)


def findPowerSum(games: list[Game]) -> int:
    return sum([findPower(g) for g in games])


if __name__ == "__main__":
    line1 = "Game 1: 3 blue, 7 green, 10 red; 4 green, 4 red; 1 green, 7 blue, 5 red; 8 blue, 10 red; 7 blue, 19 red, 1 green"
    res1 = readGame(line1)
    assert res1.idx == 1
    assert res1.reds == [10, 4, 5, 10, 19]
    assert res1.greens == [7, 4, 1, 1]
    assert res1.blues == [3, 7, 8, 7]

    game1 = Game([13], [1], [2], 1)
    assert isPossible(game1) is False
    game2 = Game([10], [1], [2], 2)
    assert isPossible(game2) is True

    assert findPower(game1) == 26
    assert findPower(game2) == 20
    assert findPower(res1) == 1064
