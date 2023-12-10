import os
from mypipes import readMap, AugmentedMap, createLoop, assignDistances, unwrapLoop, getRegionsFromFields, isSurroundedByLoop

dirname = os.path.dirname(__file__)

with open(os.path.join(dirname, 'input.txt')) as f:
    txt = f.readlines()
    lines = [line.strip() for line in txt if line.strip() != ""]
    m = readMap(lines)
    loop = createLoop(m)
    assignDistances(loop)
    unwrapped = unwrapLoop(loop)

    res = max([x.distance for x in unwrapped])
    print(f"Part1: {res}")

    augmented = AugmentedMap(m)
    regions = getRegionsFromFields(augmented)
    surrounded_regions = [x for x in regions if isSurroundedByLoop(augmented, x)]
    filtered_surrounded_regions = [[x for x in region if not x.is_pseudo] for region in surrounded_regions]
    num_surrounded_fields = sum([len(x) for x in filtered_surrounded_regions])

    print(f"Part2: {num_surrounded_fields}")
