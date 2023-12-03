spelled = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]


def readLine(line: str) -> int:
    foundSpelled: list[tuple[int, str]] = []
    for num in spelled:
        i = line.find(num)
        while i != -1:
            foundSpelled.append((line.find(num, i), num))
            i = line.find(num, i + 1)

    foundNumeric: list[tuple[int, str]] = []
    for num in range(1, 10):
        i = line.find(str(num))
        while i != -1:
            foundNumeric.append((line.find(str(num), i), str(num)))
            i = line.find(str(num), i + 1)

    spelledConverted = []
    for x in foundSpelled:
        spelledConverted.append((x[0], str(spelled.index(x[1]) + 1)))

    numbers = sorted(foundNumeric + spelledConverted, key=lambda x: x[0])

    c1 = numbers[0]
    c2 = numbers[len(numbers) - 1]
    return int(c1[1]) * 10 + int(c2[1])


def readLines(lines: list[str]) -> list[int]:
    return [readLine(line) for line in lines]


if __name__ == "__main__":
    assert readLine("one") == 11
    assert readLine("onetwo") == 12
    assert readLine("three") == 33
    assert readLine("1two") == 12
    assert readLine("1twothree") == 13
    assert readLine("sevenine") == 79

    assert readLine("sevenineonetwothree") == 73
    assert readLine("sixthree2") == 62

    lines = [
        "two1nine",
        "eightwothree",
        "abcone2threexyz",
        "xtwone3four",
        "4nineeightseven2",
        "zoneight234",
        "7pqrstsixteen",
    ]
    res = 0
    for x in readLines(lines):
        res += x
    assert res == 281
