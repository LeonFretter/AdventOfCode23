def readLine(line: str) -> int:
    chars = list(line)
    numbers = filter(lambda x: x.isnumeric(), chars)
    c1 = next(numbers)
    c2 = c1
    try:
        while True:
            c2 = next(numbers)
    except StopIteration:
        return int(c1) * 10 + int(c2)


def readLines(lines: list[str]) -> list[int]:
    return [readLine(line) for line in lines]


if __name__ == "__main__":
    assert readLine("1") == 11
    assert readLine("12") == 12
    assert readLine("123") == 13
    assert readLine("1abc2def3ghi4") == 14

    assert readLines(["1", "12", "123", "1abc2def3ghi4"]) == [11, 12, 13, 14]
