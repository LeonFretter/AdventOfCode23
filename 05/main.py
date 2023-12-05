import os 
from map import MapReader, getLocations, listChunks

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'input.txt')

with open(filename) as f:
    txt = f.read()

    mapReader = MapReader(txt)
    locations = getLocations(mapReader.seeds, mapReader.tree)

    lowestLoc = min(locations)
    print(f"Part 1: {lowestLoc}")

    seedRanges = mapReader.seedRanges
    lowestLocs: list[int] = []
    for i, rng in enumerate(seedRanges):
        print(f"Calculating part 2 for {i + 1}/{len(seedRanges)}, range {rng}")
        seeds = MapReader.seedsFromRange(rng)
        chunks = listChunks(seeds, 1000)
        for i, chunk in enumerate(chunks):
            print(f"chunk: {i} of {len(chunks)}")
            locations = getLocations(chunk, mapReader.tree)
            lowestLoc = min(locations)
            lowestLocs.append(lowestLoc)

    lowestLoc2 = min(lowestLocs)
    print(f"Part 2: {lowestLoc2}")
