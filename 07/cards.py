from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class Card:
    suit: str

    def getStrength(self, joker_rule=False) -> int:
        strengths = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", 'K', 'A']
        alternative_strengths = ["J", "2", "3", "4", "5", "6", "7", "8", "9", "T", "Q", 'K', 'A']
        if joker_rule:
            return alternative_strengths.index(self.suit) + 1
        else:
            return strengths.index(self.suit) + 1

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


def getCardTuplesWithoutJokers(cards: list[Card], joker_rule=False) -> list[CardTuple]:
    tuples: list[CardTuple] = []
    for card in cards:
        found = False
        if joker_rule and card.suit == "J":
            continue
        for t in tuples:
            if t.card == card:
                t.count += 1
                found = True
                break
        if not found:
            tuples.append(CardTuple(card))
    return tuples


def getJokers(cards: list[Card]) -> list[Card]:
    jokers = []
    for card in cards:
        if card.suit == "J":
            jokers.append(card)
    return jokers


class Hand:
    def __init__(self, cards: list[Card], joker_rule=False):
        self.joker_rule = joker_rule
        self.cards = cards
        self.tuples = getCardTuplesWithoutJokers(cards, joker_rule)
        self.tuples.sort(key=lambda t: t.count)
        if joker_rule:
            if len(self.tuples) > 0:
                self.tuples[-1].count += len(getJokers(cards))
            else:
                # we have only jokers
                self.tuples = [CardTuple(Card("J"), len(getJokers(cards)))]

    def getStrength(self) -> int:
        res = 0
        for t in self.tuples:
            tuple_stren = (1 << 18) << (2 * t.count)
            res += tuple_stren
        for i, c in enumerate(reversed(self.cards)):
            res += c.getStrength(self.joker_rule) << (i * 4)
        return res

    def __lt__(self, other: "Hand") -> bool:
        return self.getStrength() < other.getStrength()

    def __gt__(self, other: "Hand") -> bool:
        return self.getStrength() > other.getStrength()

    def __str__(self) -> str:
        return "".join([c.suit for c in self.cards])

    def isFullHouse(self) -> bool:
        return any(tuple.count == 3 for tuple in self.tuples) and any(tuple.count == 2 for tuple in self.tuples)

    def isFiveOfAKind(self) -> bool:
        return any(tuple.count == 5 for tuple in self.tuples)

    def isFourOfAKind(self) -> bool:
        return any(tuple.count == 4 for tuple in self.tuples)

    def isThreeOfAKind(self) -> bool:
        return not self.isFullHouse() and any(tuple.count == 3 for tuple in self.tuples)

    def isTwoPair(self) -> bool:
        return len([tuple for tuple in self.tuples if tuple.count == 2]) == 2

    def isOnePair(self) -> bool:
        return len([tuple for tuple in self.tuples if tuple.count == 2]) == 1

    def isHighCard(self) -> bool:
        return len(self.tuples) == 5


@dataclass
class Player:
    hand: Hand
    bid: int

    def __lt__(self, other: "Player") -> bool:
        return self.hand < other.hand

    def __gt__(self, other: "Player") -> bool:
        return self.hand > other.hand


def parsePlayer(line: str, joker_rule=False) -> Player:
    cards_txt, bid_txt = line.split(" ")
    cards = parseCards(cards_txt)
    hand = Hand(cards, joker_rule)
    bid = int(bid_txt)
    return Player(hand, bid)


class Game:
    def __init__(self, players: list[Player]) -> None:
        self.players = sorted(players)

    def getScore(self) -> int:
        return sum([p.bid * (i + 1) for i, p in enumerate(self.players)])


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
    res_hands = [str(p.hand) for p in example_players_2]
    assert res_hands == expected_hands
    example_game_2 = Game(example_players_2)
    assert example_game_2.getScore() == 6440

    example_players_2_with_joker = [
        Player(Hand(parseCards("32T3K"), True), 765),
        Player(Hand(parseCards("T55J5"), True), 684),
        Player(Hand(parseCards("KK677"), True), 28),
        Player(Hand(parseCards("KTJJT"), True), 220),
        Player(Hand(parseCards("QQQJA"), True), 483),
    ]

    example_players_2_with_joker.sort()
    expected_hands = ["32T3K", "KK677", "T55J5", "QQQJA", "KTJJT"]
    res_hands = [str(p.hand) for p in example_players_2_with_joker]
    assert res_hands == expected_hands
    example_game_2_with_joker = Game(example_players_2_with_joker)
    assert example_game_2_with_joker.getScore() == 5905

    example_hands_2_txt = [
        "JJJJJ",
        "22222",
        "J2222",
        "2222J",
    ]
    example_hands_2 = [Hand(parseCards(txt), True) for txt in example_hands_2_txt]
    example_scores = [h.getStrength() for h in example_hands_2]
    example_hands_2.sort()
    expected_hands = ["JJJJJ", "J2222", "2222J", "22222"]
    res_hands = [str(h) for h in example_hands_2]
    assert res_hands == expected_hands

    example_hands_3_txt = [
        "2233J",
        "22J33",
        "J3322",
        "J2233",
    ]
    example_hands_3 = [Hand(parseCards(txt), True) for txt in example_hands_3_txt]
    example_hands_3.sort()
    expected_hands = ["J2233", "J3322", "22J33", "2233J"]
    example_full_houses = [h for h in example_hands_3 if h.isFullHouse()]
    example_full_houses_txt = [str(h) for h in example_full_houses]
    assert example_full_houses_txt == expected_hands
    res_hands = [str(h) for h in example_hands_3]
    assert res_hands == expected_hands

    three_of_kinds = Hand(parseCards("2234J"), True)
    assert three_of_kinds.isThreeOfAKind()
    assert not three_of_kinds.isFullHouse()
    assert not three_of_kinds.isTwoPair()
