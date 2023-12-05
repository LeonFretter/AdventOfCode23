from dataclasses import dataclass


@dataclass
class Map:
    dst_range_start: int
    src_range_start: int
    range_length: int

    def inRange(self, source: int) -> bool:
        return source >= self.src_range_start and source < self.src_range_start + self.range_length

    def getDestination(self, source: int) -> int:
        if source < self.src_range_start:
            raise ValueError("Source is too small")
        if source >= self.src_range_start + self.range_length:
            raise ValueError("Source is too large")
        return self.dst_range_start + (source - self.src_range_start)


class MultiMap:
    def __init__(self, maps: list[Map]) -> None:
        maps.sort(key=lambda x: x.src_range_start)
        self.maps = maps

    def getDestination(self, source: int) -> int | None:
        for map in self.maps:
            if map.inRange(source):
                return map.getDestination(source)
        return None

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


def findBetween(s: str, start: str, end: str) -> str:
    return s.split(start)[1].split(end)[0]


def listChunks[T](initial: list[T], sz: int) -> list[list[T]]:
    return [initial[i: min(i + sz, len(initial))] for i in range(0, len(initial), sz)]


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

        self.seeds = MapReader.parseSeeds(seeds_txt)
        self.seedRanges = MapReader.parseSeedRanges(seeds_txt)
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

    @staticmethod
    def parseSeeds(seed_txt: str) -> list[int]:
        return [int(s) for s in seed_txt.strip().split(" ")]

    @staticmethod
    def parseSeedRanges(seed_text: str) -> list[tuple[int, int]]:
        nums = seed_text.strip().split(" ")
        ranges = listChunks(nums, 2)
        ranges.sort(key=lambda x: int(x[0]))
        res_ranges: list[tuple[int, int]] = []
        for r in ranges:
            res_ranges.append((int(r[0]), int(r[1])))
        return res_ranges

    @staticmethod
    def seedsFromRange(rng: tuple[int, int]) -> list[int]:
        ra, rb = rng
        return list(range(ra, ra + rb))

    @staticmethod
    def seedsFromRanges(rngs: list[tuple[int, int]]) -> list[int]:
        seeds: list[int] = []
        for rng in rngs:
            seeds.extend(MapReader.seedsFromRange(rng))
        return seeds


def getLocations(seeds: list[int], tree: Tree) -> list[int]:
    locations: list[int] = []
    for seed in seeds:
        path = tree.getPath(seed)
        locations.append(path[-1])
    return locations


if __name__ == "__main__":
    exampleMap = Map(50, 98, 2)
    assert exampleMap.getDestination(98) == 50
    assert exampleMap.getDestination(99) == 51

    exampleMap2 = Map(0, 15, 37)
    assert exampleMap2.getDestination(15) == 0
    assert exampleMap2.getDestination(16) == 1

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

    examplePath2 = exampleTree.getPath(3)
    assert examplePath2 == [3, 1, 11]

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

    expectedLocations = [82, 43, 86, 35]
    assert getLocations(seeds, tree) == expectedLocations

    exampleRangeTxt = "0 4 4 5 9 2"
    exampleRanges = MapReader.parseSeedRanges(exampleRangeTxt)
    exampleRangeSeeds = MapReader.seedsFromRanges(exampleRanges)
    assert exampleRangeSeeds == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
