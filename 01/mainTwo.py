from readLinesTwo import readLines

with open('input.txt', 'r') as f:
    lines = f.readlines()
    lines = [line.strip() for line in lines]
    lines = readLines(lines)

    res = 0
    for x in lines:
        res += x
    print(res)
