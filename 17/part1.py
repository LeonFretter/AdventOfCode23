import sys
import os
from path import readMapWithCostToReach, traverseFromStart

args = sys.argv[1:]

dirname = os.path.dirname(__file__)

upper_bound = sys.maxsize
if len(args) > 1:
    upper_bound = int(args[0])

f_naive_costs = open(os.path.join(dirname, 'naive_costs.txt'))
naive_costs = f_naive_costs.read()
f_input = open(os.path.join(dirname, 'input.txt'))
map_txt = f_input.read()
f_cost_to_reach = open(os.path.join(dirname, 'cost_to_reach.txt'))
cost_to_reach = f_cost_to_reach.read()

m = readMapWithCostToReach(map_txt, naive_costs, cost_to_reach)
traverseFromStart(m, upper_bound)
print(m.costToReachStr())
f3 = open(os.path.join(dirname, 'cost_to_reach.txt'), "w")
f3.write(m.costToReachStr())
