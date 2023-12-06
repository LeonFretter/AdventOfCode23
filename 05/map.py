from dataclasses import dataclass


@dataclass
class Map:
    dst_range_start: int
    src_range_start: int
    range_length: int

    def inRange(self, source: int) -> bool:
        return source >= self.src_range_start and source < self.src_range_start + self.range_length

    def dstInRange(self, dst: int) -> bool:
        return dst >= self.dst_range_start and dst < self.dst_range_start + self.range_length

    def getDestination(self, source: int) -> int:
        if source < self.src_range_start:
            raise ValueError("Source is too small")
        if source >= self.src_range_start + self.range_length:
            raise ValueError("Source is too large")
        return self.dst_range_start + (source - self.src_range_start)

    def getSource(self, dst: int) -> int:
        if dst < self.dst_range_start:
            raise ValueError("Destination is too small")
        if dst >= self.dst_range_start + self.range_length:
            raise ValueError("Destination is too large")
        return self.src_range_start + (dst - self.dst_range_start)


class MultiMap:
    def __init__(self, maps: list[Map]) -> None:
        maps.sort(key=lambda x: x.src_range_start)
        self.maps = maps

    def getDestination(self, source: int) -> int | None:
        for map in self.maps:
            if map.inRange(source):
                return map.getDestination(source)
        return None

    def getSource(self, dst: int) -> int | None:
        for map in self.maps:
            if map.dstInRange(dst):
                return map.getSource(dst)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MultiMap):
            return False
        return self.maps == other.maps


@dataclass
class Tree:
    map_layers: list[MultiMap]

    def getPath(self, root: int) -> list[int]:
        path = [root]
        current_node = root
        next_node = None
        for layer in self.map_layers:
            next_node = layer.getDestination(current_node)
            if next_node is None:
                next_node = current_node
            path.append(next_node)
            current_node = next_node
        return path

    def getReversePath(self, leaf: int) -> list[int]:
        path = [leaf]
        current_node = leaf
        next_node = None
        for layer in reversed(self.map_layers):
            next_node = layer.getSource(current_node)
            if next_node is None:
                next_node = current_node
            path.append(next_node)
            current_node = next_node
        return path


def findBetween(s: str, start: str, end: str) -> str:
    return s.split(start)[1].split(end)[0]


class MapReader:
    def __init__(self, txt: str) -> None:
        seeds_txt = findBetween(txt, "seeds:", "\n")
        seed_to_soil_txt = findBetween(txt, "seed-to-soil map:", "soil-to-fertilizer map:")
        soil_to_fertilizer_txt = findBetween(txt, "soil-to-fertilizer map:", "fertilizer-to-water map:")
        fertilizer_to_water_txt = findBetween(txt, "fertilizer-to-water map:", "water-to-light map:")
        water_to_light_txt = findBetween(txt, "water-to-light map:", "light-to-temperature map:")
        light_to_temperature_txt = findBetween(txt, "light-to-temperature map:", "temperature-to-humidity map:")
        temperature_to_humidity_txt = findBetween(txt, "temperature-to-humidity map:", "humidity-to-location map:")
        humidity_to_location_txt = txt.split("humidity-to-location map:")[1]

        self.seeds = self.parseSeeds(seeds_txt)
        self.seed_ranges = self.parseSeedRanges(seeds_txt)
        seed_to_soil = self.parseMap(seed_to_soil_txt)
        soil_to_fertilizer = self.parseMap(soil_to_fertilizer_txt)
        fertilizer_to_water = self.parseMap(fertilizer_to_water_txt)
        water_to_light = self.parseMap(water_to_light_txt)
        light_to_temperature = self.parseMap(light_to_temperature_txt)
        temperature_to_humidity = self.parseMap(temperature_to_humidity_txt)
        humidity_to_location = self.parseMap(humidity_to_location_txt)

        self.tree = Tree([
            seed_to_soil,
            soil_to_fertilizer,
            fertilizer_to_water,
            water_to_light,
            light_to_temperature,
            temperature_to_humidity,
            humidity_to_location
        ])

    def parseMap(self, map_txt: str) -> MultiMap:
        maps = []
        for line in map_txt.splitlines():
            if line.strip() == "":
                continue
            parts = line.split(" ")
            dst_range_start = int(parts[0])
            src_range_start = int(parts[1])
            range_length = int(parts[2])
            maps.append(Map(dst_range_start, src_range_start, range_length))
        return MultiMap(maps)

    def parseSeeds(self, seed_txt: str) -> list[int]:
        return [int(s) for s in seed_txt.strip().split(" ")]

    def parseSeedRanges(self, seed_txt: str) -> list[tuple[int, int]]:
        seed_ranges = []
        parts = seed_txt.strip().split(" ")
        for i in range(0, len(parts), 2):
            seed_ranges.append((int(parts[i]), int(parts[i + 1])))
        return seed_ranges


def getLocations(seeds: list[int], tree: Tree) -> list[int]:
    locations: list[int] = []
    for seed in seeds:
        path = tree.getPath(seed)
        locations.append(path[-1])
    return locations


def containsSeed(range: tuple[int, int], seed: int) -> bool:
    return seed >= range[0] and seed < range[0] + range[1]


def getSeedFromLocation(location: int, tree: Tree) -> int:
    path = tree.getReversePath(location)
    return path[-1]


if __name__ == "__main__":
    exampleMap = Map(50, 98, 2)
    assert exampleMap.getDestination(98) == 50
    assert exampleMap.getDestination(99) == 51
    assert exampleMap.getSource(50) == 98
    assert exampleMap.getSource(51) == 99

    exampleMap2 = Map(0, 15, 37)
    assert exampleMap2.getDestination(15) == 0
    assert exampleMap2.getDestination(16) == 1
    assert exampleMap2.getSource(0) == 15
    assert exampleMap2.getSource(1) == 16

    exampleTree = Tree(
        [
            MultiMap(
                [
                    Map(0, 2, 2),
                ],
            ),
            MultiMap(
                [
                    Map(10, 0, 2)
                ]
            )
        ]
    )

    examplePath1 = exampleTree.getPath(2)
    assert examplePath1 == [2, 0, 10]
    exampleReversePath1 = exampleTree.getReversePath(10)
    assert exampleReversePath1 == [10, 0, 2]
    exampleSeed1 = getSeedFromLocation(10, exampleTree)
    assert exampleSeed1 == 2

    examplePath2 = exampleTree.getPath(3)
    assert examplePath2 == [3, 1, 11]
    exampleReversePath2 = exampleTree.getReversePath(11)
    assert exampleReversePath2 == [11, 1, 3]
    exampleSeed2 = getSeedFromLocation(11, exampleTree)
    assert exampleSeed2 == 3

    txt = """
seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48

soil-to-fertilizer map:
0 15 37
37 52 2
39 0 15

fertilizer-to-water map:
49 53 8
0 11 42
42 0 7
57 7 4

water-to-light map:
88 18 7
18 25 70

light-to-temperature map:
45 77 23
81 45 19
68 64 13

temperature-to-humidity map:
0 69 1
1 0 69

humidity-to-location map:
60 56 37
56 93 4
"""
    reader = MapReader(txt)
    seeds = reader.seeds
    tree = reader.tree
    assert tree == Tree(
        [
            MultiMap(
                [
                    Map(50, 98, 2),
                    Map(52, 50, 48)
                ]
            ),
            MultiMap(
                [
                    Map(0, 15, 37),
                    Map(37, 52, 2),
                    Map(39, 0, 15)
                ]
            ),
            MultiMap(
                [
                    Map(49, 53, 8),
                    Map(0, 11, 42),
                    Map(42, 0, 7),
                    Map(57, 7, 4)
                ]
            ),
            MultiMap(
                [
                    Map(88, 18, 7),
                    Map(18, 25, 70)
                ]
            ),
            MultiMap(
                [
                    Map(45, 77, 23),
                    Map(81, 45, 19),
                    Map(68, 64, 13)
                ]
            ),
            MultiMap(
                [
                    Map(0, 69, 1),
                    Map(1, 0, 69)
                ]
            ),
            MultiMap(
                [
                    Map(60, 56, 37),
                    Map(56, 93, 4)
                ]
            )
        ]
    )
    examplePath = tree.getPath(0)
    assert examplePath == [0, 0, 39, 28, 21, 21, 22, 22]
    exampleReversePath = tree.getReversePath(22)
    assert exampleReversePath == [22, 22, 21, 21, 28, 39, 0, 0]
    assert getSeedFromLocation(22, tree) == 0

    expectedLocations = [82, 43, 86, 35]
    assert getLocations(seeds, tree) == expectedLocations

    exampleSeedRange = (15, 10)
    assert containsSeed(exampleSeedRange, 15)
    assert containsSeed(exampleSeedRange, 24)
    assert not containsSeed(exampleSeedRange, 14)
    assert not containsSeed(exampleSeedRange, 25)
