import os
from universe import createPositionMap, findGalaxies, countSteps

dirname = os.path.dirname(__file__)

with open(os.path.join(dirname, 'input.txt')) as f:
    lines = f.readlines()

    universe = lines
    positions = createPositionMap(lines, 2)
    galaxies = findGalaxies(universe, positions)
    steps = countSteps(galaxies)

    print(f"Part 1: {steps}")

    positions = createPositionMap(lines, 1000000)
    galaxies = findGalaxies(universe, positions)
    steps = countSteps(galaxies)

    print(f"Part 2: {steps}")
