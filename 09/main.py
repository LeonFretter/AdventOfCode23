import os
from seq import readSequences, extrapolate, getRecursiveDifferences, extrapolateBackwards

dirname = os.path.dirname(__file__)

with open(os.path.join(dirname, 'input.txt')) as f:
    txt = f.read()
    sequences = readSequences(txt)
    extrapolated = [extrapolate(getRecursiveDifferences(x)) for x in sequences]
    res = sum(extrapolated)

    print(f"Part 1: {res}")

    backwards_extrapolated = [extrapolateBackwards(getRecursiveDifferences(x)) for x in sequences]
    res_2 = sum(backwards_extrapolated)

    print(f"Part 2: {res_2}")
