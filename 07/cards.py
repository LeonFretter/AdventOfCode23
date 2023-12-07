from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class Card:
    suit: str

    def getStrength(self) -> int:
        strengths = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", 'K', 'A']
        return strengths.index(self.suit)

    def __eq__(self, other: "Card") -> bool:
        return self.suit == other.suit


def parseCards(txt: str) -> list[Card]:
    cards: list[Card] = []
    for c in txt:
        cards.append(Card(c))
    return cards


@dataclass
class CardTuple:
    card: Card
    count: int = 1


def getCardTuples(cards: list[Card]) -> list[CardTuple]:
    tuples: list[CardTuple] = []
    for card in cards:
        found = False
        for t in tuples:
            if t.card == card:
                t.count += 1
                found = True
                break
        if not found:
            tuples.append(CardTuple(card))
    return tuples


class Hand:
    def __init__(self, cards: list[Card]):
        self.cards = cards
        self.tuples = getCardTuples(cards)

    def getStrength(self) -> int:
        res = 0
        for t in self.tuples:
            tuple_stren = (1 << 18) << (2 * t.count)
            res += tuple_stren
        for i, c in enumerate(reversed(self.cards)):
            res += c.getStrength() << (i * 4)
        return res

    def __lt__(self, other: "Hand") -> bool:
        return self.getStrength() < other.getStrength()

    def __gt__(self, other: "Hand") -> bool:
        return self.getStrength() > other.getStrength()

    def __str__(self) -> str:
        return "".join([c.suit for c in self.cards])


@dataclass
class Player:
    hand: Hand
    bid: int

    def __lt__(self, other: "Player") -> bool:
        return self.hand < other.hand

    def __gt__(self, other: "Player") -> bool:
        return self.hand > other.hand


def parsePlayer(line: str) -> Player:
    cards_txt, bid_txt = line.split(" ")
    cards = parseCards(cards_txt)
    hand = Hand(cards)
    bid = int(bid_txt)
    return Player(hand, bid)


@dataclass
class Game:
    players: list[Player]

    def getScore(self) -> int:
        sorted_players = sorted(self.players)
        return sum([p.bid * (i + 1) for i, p in enumerate(sorted_players)])


if __name__ == "__main__":
    example_card_txts = [
        "22233",
        "33222",
        "AAAKQ",
        "KKKKQ",
        "22222"
    ]

    example_cards = [parseCards(txt) for txt in example_card_txts]
    example_hands = [Hand(cards) for cards in example_cards]
    example_hands.sort()

    example_hands_txt = [str(h) for h in example_hands]
    assert example_hands_txt == ["AAAKQ", "22233", "33222", "KKKKQ", "22222"]

    example_players = [
        Player(Hand(parseCards("22233")), 8),
        Player(Hand(parseCards("33222")), 16),
    ]
    example_game = Game(example_players)
    assert example_game.getScore() == 32 + 8

    example_players_2 = [
        Player(Hand(parseCards("32T3K")), 765),
        Player(Hand(parseCards("T55J5")), 684),
        Player(Hand(parseCards("KK677")), 28),
        Player(Hand(parseCards("KTJJT")), 220),
        Player(Hand(parseCards("QQQJA")), 483),
    ]
    example_players_2.sort()
    expected_hands = ["32T3K", "KTJJT", "KK677", "T55J5", "QQQJA"]
    res_hands =  [str(p.hand) for p in example_players_2] 
    assert res_hands == expected_hands
    example_game_2 = Game(example_players_2)
    print(example_game_2.getScore())
    assert example_game_2.getScore() == 6440
