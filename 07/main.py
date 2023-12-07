import os
from cards import parsePlayer, Game

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'input.txt')

with open(filename) as f:
    lines = f.readlines()

    players = [parsePlayer(line) for line in lines]
    game = Game(players)

    print(f"Part 1: {game.getScore()}")
