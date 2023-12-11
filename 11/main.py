import os
from universe import createExpandedUniverse, findGalaxies, countSteps

dirname = os.path.dirname(__file__)

with open(os.path.join(dirname, 'input.txt')) as f:
    lines = f.readlines()

    universe = createExpandedUniverse(lines)
    galaxies = findGalaxies(universe)
    steps = countSteps(galaxies)

    print(f"Part 1: {steps}")
