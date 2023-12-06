import os
from boat import readRaces, joinRaces

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'input.txt')

with open(filename) as f:
    counts: list[int] = []
    races = readRaces(f.readlines())
    for r in races:
        counts.append(r.countWinners())

    res = 1
    for c in counts:
        res *= c

    print(f"Part 1: {res}")

    joined_race = joinRaces(races)
    count2 = joined_race.countWinners()

    print(f"Part 2: {count2}")
