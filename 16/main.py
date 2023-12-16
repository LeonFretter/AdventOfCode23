import os
from beams import countEnergized, createBeams, readMap

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, "input.txt")

with open(filename) as f:
    txt = f.read()
    m = readMap(txt)
    beams = createBeams(m)
    print(m)
    count = countEnergized(m)
    print(count)
