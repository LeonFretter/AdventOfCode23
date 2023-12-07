import os
from cards import parsePlayer, Game

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'input.txt')

with open(filename) as f:
    lines = f.readlines()

    players = [parsePlayer(line) for line in lines]
    game = Game(players)

    print(f"Part 1: {game.getScore()}")

    players_with_joker = [parsePlayer(line, True) for line in lines]
    game_with_joker = Game(players_with_joker)

    print(f"Part 2: {game_with_joker.getScore()}")
