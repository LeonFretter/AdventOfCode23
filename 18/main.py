import os
from dig import readInstructions, getNodes, Vec2, createBoundaryMap, fillBoundaryMap

dirname = os.path.dirname(__file__)

with open(os.path.join(dirname, "input.txt")) as input:
    txt = input.read()
    instructions = readInstructions(txt)
    nodes = getNodes(instructions)
    boundary_map = createBoundaryMap(nodes)

    boundary_map_f = open(os.path.join(dirname, "boundary_map.txt"), "w")
    boundary_map_f.write(str(boundary_map))
    boundary_map_f.close()

    filled_map = fillBoundaryMap(boundary_map, Vec2(26, 84))
    
    filled_map_f = open(os.path.join(dirname, "filled_map.txt"), "w")
    filled_map_f.write(str(filled_map))
    filled_map_f.close()

    count = int(filled_map)
    print(f"Part 1: {count}")
