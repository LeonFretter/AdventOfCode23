from dataclasses import dataclass


@dataclass
class Line:
    schematic: str
    sequence: list[int]


def readLine(line: str) -> Line:
    schematic, sequence_txt = line.split(" ")
    sequence = [int(x) for x in sequence_txt.split(",")]
    return Line(schematic, sequence)


def readSchematicValue(schematic: str, idx: int) -> tuple[int, int]:
    x = 0
    for i in range(idx, len(schematic)):
        idx = i
        if schematic[i] == "#":
            x += 1
        else:
            break
    return x, idx + 1


def readSchematicSequence(schematic: str) -> list[int]:
    sequences = []
    idx = 0
    while idx < len(schematic):
        x, idx = readSchematicValue(schematic, idx)
        sequences.append(x)
    sequences = [x for x in sequences if x > 0]
    return sequences


def matches(schematic: str, sequence: list[int]) -> bool:
    schematic_seq = readSchematicSequence(schematic)
    return schematic_seq == sequence


def createSchematicVariants(schematic: str) -> list[str]:
    variants: list[str] = []
    variant_count = len([c for c in schematic if c == "?"])

    for i in range(2 ** variant_count):
        variant = ""
        wildcard_idx = 0
        for c in schematic:
            if c == "?":
                if i & (1 << wildcard_idx):
                    variant += "#"
                else:
                    variant += "."
                wildcard_idx += 1
            else:
                variant += c
        variants.append(variant)
    return variants


@dataclass
class VariantLine:
    original_schematic: str
    variants: list[str]
    sequence: list[int]

    def countMatches(self) -> int:
        return len([v for v in self.variants if matches(v, self.sequence)])


def createVariantLine(line: Line) -> VariantLine:
    variants = createSchematicVariants(line.schematic)
    return VariantLine(line.schematic, variants, line.sequence)


if __name__ == "__main__":
    example_schematic = "##.#...###.#"
    res_example_seq = readSchematicSequence(example_schematic)
    assert res_example_seq == [2, 1, 3, 1]

    txt = """
???.### 1,1,3
.??..??...?##. 1,1,3
?#?#?#?#?#?#?#? 1,3,1,6
????.#...#... 4,1,1
????.######..#####. 1,6,5
?###???????? 3,2,1
"""
    txt_lines = [line for line in txt.split("\n") if line != ""]
    lines = [readLine(line) for line in txt_lines]
    variant_lines = [createVariantLine(line) for line in lines]
    num_matches = [line.countMatches() for line in variant_lines]

    print(num_matches)
    total_num_matches = sum(num_matches)
    print(total_num_matches)
    assert total_num_matches == 21
