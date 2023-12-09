def readSequence(line: str) -> list[int]:
    return [int(x.strip()) for x in line.split(" ")]


def readSequences(lines: str) -> list[list[int]]:
    return [readSequence(line) for line in lines.split("\n") if line.strip() != ""]


def getDifferences(sequence: list[int]) -> list[int]:
    return [sequence[i] - sequence[i - 1] for i in range(1, len(sequence))]


def getRecursiveDifferences(sequence: list[int]) -> list[list[int]]:
    res: list[list[int]] = [sequence]
    diff = getDifferences(sequence)
    while not all([x == 0 for x in diff]):
        res.append(diff)
        diff = getDifferences(diff)
    res.append(diff)

    return res


def extrapolate(elems: list[list[int]]) -> int:
    elems[-1].append(0)
    for i in range(len(elems) - 2, -1, -1):
        l = elems[i]
        diff = elems[i + 1][-1]
        l.append(l[-1] + diff)
    return elems[0][-1]


def extrapolateBackwards(elems: list[list[int]]) -> int:
    elems[-1].insert(0, 0)
    for i in range(len(elems) - 2, -1, -1):
        l = elems[i]
        diff = elems[i + 1][0]
        l.insert(0, l[0] - diff)
    return elems[0][0]


if __name__ == "__main__":
    example_txt = """
0 3 6 9 12 15
1 3 6 10 15 21
10 13 16 21 30 45
"""
    example = readSequences(example_txt)

    extrapolated = [extrapolate(getRecursiveDifferences(x)) for x in example]
    assert extrapolated == [18, 28, 68]
    res = sum(extrapolated)
    assert res == 114

    backwards_extrapolated = [extrapolateBackwards(getRecursiveDifferences(x)) for x in example]
    assert backwards_extrapolated == [-3, 0, 5]
    res = sum(backwards_extrapolated)
    assert res == 2
