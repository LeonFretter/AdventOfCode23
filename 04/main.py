import os
from card import Card, readCard, duplicateCards, countCards

dirname = os.path.dirname(__file__)
inputFile = os.path.join(dirname, 'input.txt')

with open(inputFile) as f:
    lines = f.read().splitlines()
    cards = [readCard(line) for line in lines]
    resScore = sum([card.getScore() for card in cards])

    print(f"Part 1: {resScore}")

    withDuplicates = duplicateCards(cards)
    n = countCards(withDuplicates)
    print(f"Part 2: {n}")
