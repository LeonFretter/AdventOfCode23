from dataclasses import dataclass


@dataclass
class Map:
    dst_range_start: int
    src_range_start: int
    range_length: int

    def getDestination(self, source: int) -> int:
        if source < self.src_range_start:
            raise ValueError("Source is too small")
        if source >= self.src_range_start + self.range_length:
            raise ValueError("Source is too large")
        return self.dst_range_start + (source - self.src_range_start)


@dataclass
class MultiMap:
    maps: list[Map]

    def getDestinations(self, source: int) -> list[int]:
        res: list[int] = []
        for m in self.maps:
            try:
                res.append(m.getDestination(source))
            except ValueError:
                pass
        return res


def findBetween(s: str, start: str, end: str) -> str:
    return s.split(start)[1].split(end)[0]


@dataclass
class Tree:
    map_layers: list[MultiMap]

    def getLeaves(self, root: int) -> list[int]:
        current_layer: list[int] = [root]
        next_layer: list[int] = []
        for layer in self.map_layers:
            for node in current_layer:
                next_layer.extend(layer.getDestinations(node))
            current_layer = next_layer
        return next_layer


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


def getLocations(seeds: list[int], tree: Tree) -> list[tuple[int, list[int]]]:
    locations: list[tuple[int, list[int]]] = []
    for seed in seeds:
        locations.append((seed, tree.getLeaves(seed)))
    return locations


if __name__ == "__main__":
    exampleMap = Map(50, 98, 2)
    assert exampleMap.getDestination(98) == 50
    assert exampleMap.getDestination(99) == 51

    exampleMap2 = Map(0, 15, 37)
    assert exampleMap2.getDestination(15) == 0
    assert exampleMap2.getDestination(16) == 1

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
    l1 = tree.getLeaves(0)
    assert tree.getLeaves(0) == [0]
    assert tree.getLeaves(69) == [98]
    assert tree.getLeaves(97) == [99]
    assert tree.getLeaves(98) == [50]
    assert tree.getLeaves(99) == [51]
