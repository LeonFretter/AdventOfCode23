import os 
from map import MapReader, getLocations

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'input.txt')

with open(filename) as f:
    txt = f.read()

    mapReader = MapReader(txt)
    locations = getLocations(mapReader.seeds, mapReader.tree)

    lowestLoc = min(locations)
    print(lowestLoc)
