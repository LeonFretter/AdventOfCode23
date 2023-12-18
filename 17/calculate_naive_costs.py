import os
from path import readMap

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'input.txt')

with open(filename) as f:
    txt = f.read()

    m = readMap(txt)
    m.assignNaiveCosts(m.goal_node)

    f2 = open("naive_costs.txt", "w")
    f2.write(m.naiveCostsStr())
