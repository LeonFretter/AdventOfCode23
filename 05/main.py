import os
from map import MapReader, getLocations, getSeedFromLocation, containsSeed
from sys import argv

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'input.txt')
args = argv[1:]

with open(filename) as f:
    txt = f.read()

    mapReader = MapReader(txt)
    locations = getLocations(mapReader.seeds, mapReader.tree)

    lowestLoc = min(locations)
    print(lowestLoc)

    # part 2
    seed_ranges = mapReader.seed_ranges
    seed_ranges.sort(key=lambda r: r[0])
    first_seed = seed_ranges[0][0]
    last_seed = seed_ranges[-1][0] + seed_ranges[-1][1]
    i = 0
    print_freq = 1000
    if len(args) > 0:
        i = int(args[0])
    while True:
        seed = getSeedFromLocation(i, mapReader.tree)
        if seed >= first_seed and seed <= last_seed:
            for rng in seed_ranges:
                if containsSeed(rng, seed):
                    print(f"Lowest location is {i} for seed {seed}")
                    exit(0)
        if i % print_freq == 0:
            print(f"Current location: {i}")
        i += 1
