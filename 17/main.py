import os
from path import readMap, traverseFromStart

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'input.txt')

with open(filename) as f:
    txt = f.read()

    m = readMap(txt)
    traverseFromStart(m)
