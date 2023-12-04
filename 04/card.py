from dataclasses import dataclass


@dataclass
class Card:
    idx: int
    winning: list[int]
    user: list[int]

    def getScore(self) -> int:
        score = 0
        for u in self.user:
            if u in self.winning:
                if score == 0:
                    score = 1
                else:
                    score *= 2
        return score


def readCard(line: str) -> Card:
    idxStr, rest = line.split(':')
    idx = int(idxStr.split(' ')[-1])

    winningStr, userStr = rest.split('|')
    winning = [int(x) for x in winningStr.split(' ') if x != '']
    user = [int(x) for x in [y.strip() for y in userStr.split(' ')] if x != '']

    return Card(idx, winning, user)


if __name__ == "__main__":
    line1 = "Card 1: 1 2 3 | 4 5  6"
    card1 = readCard(line1)
    assert card1.idx == 1
    assert card1.winning == [1, 2, 3]
    assert card1.user == [4, 5, 6]

    lines = [
        "Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53",
        "Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19",
        "Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1",
        "Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83",
        "Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36",
        "Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11",
    ]

    cards = [readCard(line) for line in lines]
    resScore = sum([card.getScore() for card in cards])
    assert resScore == 13
