def splitAt(row: str, idx: int) -> tuple[str, str]:
    return row[:idx], row[idx:]


def isRowMirror(row: str, idx: int) -> bool:
    prev, after = splitAt(row, idx)
    prev = prev[::-1]
    for i in range(min(len(prev), len(after))):
        if prev[i] != after[i]:
            return False
    return True


def findRowMirrors(row: str) -> list[int]:
    res = []
    for i in range(1, len(row)):
        if isRowMirror(row, i):
            res.append(i)
    return res


type Block = list[str]


def findBlockRowMirrors(block: Block) -> list[int]:
    candidates = findRowMirrors(block[0])
    for row in block[1:]:
        candidates = [c for c in candidates if isRowMirror(row, c)]
    return candidates


def findBlockColumnMirros(block: Block) -> list[int]:
    transposed_block: list[str] = []
    for i in range(len(block[0])):
        transposed_block.append("".join([row[i] for row in block]))
    return findBlockRowMirrors(transposed_block)


def findBlockMirrors(block: Block) -> tuple[list[int], list[int]]:
    return findBlockRowMirrors(block), findBlockColumnMirros(block)


def findCleanBlockMirrors(old_new_block: tuple[Block, Block]) -> tuple[list[int], list[int]]:
    old_block, new_block = old_new_block
    old_row_mirrors, old_column_mirrors = findBlockMirrors(old_block)
    new_row_mirrors, new_column_mirrors = findBlockMirrors(new_block)
    for row_mirror in old_row_mirrors:
        if row_mirror in new_row_mirrors:
            new_row_mirrors.remove(row_mirror)
    for column_mirror in old_column_mirrors:
        if column_mirror in new_column_mirrors:
            new_column_mirrors.remove(column_mirror)
    return new_row_mirrors, new_column_mirrors


def readBlocks(txt: str) -> list[Block]:
    lines = txt.strip().split("\n")
    blocks: list[Block] = []
    block: Block = []
    for line in lines:
        if line == "":
            blocks.append(block)
            block = []
        else:
            block.append(line)
    blocks.append(block)
    return blocks


def calculateMirrorValue(blocks: list[Block]) -> int:
    res = 0
    for block in blocks:
        row_mirrors, column_mirrors = findBlockMirrors(block)
        for m in row_mirrors:
            res += m
        for m in column_mirrors:
            res += m * 100
    return res


def calculateCleanMirrorValue(blocks: list[tuple[Block, Block]]) -> int:
    res = 0
    for block in blocks:
        row_mirrors, column_mirrors = findCleanBlockMirrors(block)
        for m in row_mirrors:
            res += m
        for m in column_mirrors:
            res += m * 100
    return res


def clearSmudge(block: Block) -> tuple[Block, Block]:
    block_row_mirrors, block_column_mirrors = findBlockMirrors(block)
    new_block = block.copy()
    for row_idx, row in enumerate(new_block):
        for col_idx, char in enumerate(row):
            old_row = row
            if char == "#":
                new_block[row_idx] = row[:col_idx] + "." + row[col_idx + 1:]
            else:
                new_block[row_idx] = row[:col_idx] + "#" + row[col_idx + 1:]
            new_block_row_mirrors, new_block_column_mirrors = findBlockMirrors(new_block)
            if len(new_block_row_mirrors) > 0 or len(new_block_column_mirrors) > 0:
                if new_block_row_mirrors != block_row_mirrors or new_block_column_mirrors != block_column_mirrors:
                    return block, new_block
            new_block[row_idx] = old_row
    raise Exception("No smudge found")


if __name__ == "__main__":
    split_row = splitAt("abba", 2)
    assert split_row == ("ab", "ba")
    assert isRowMirror("abba", 2)
    assert not isRowMirror("abba", 1)
    assert findRowMirrors("abba") == [2]
    assert findRowMirrors("abccba") == [3]
    assert findBlockRowMirrors(["abba", "baab"]) == [2]
    assert findBlockColumnMirros([
        "ab",
        "ba",
        "ba",
        "ab",
    ]) == [2]

    example_txt = """
#.##..##.
..#.##.#.
##......#
##......#
..#.##.#.
..##..##.
#.#.##.#.

#...##..#
#....#..#
..##..###
#####.##.
#####.##.
..##..###
#....#..#
"""
    blocks = readBlocks(example_txt)
    assert len(blocks) == 2
    value = calculateMirrorValue(blocks)
    assert value == 405

    cleaned_blocks = [clearSmudge(block) for block in blocks]
    mirrors = [findCleanBlockMirrors(block) for block in cleaned_blocks]
    new_value = calculateCleanMirrorValue(cleaned_blocks)
    assert new_value == 400
