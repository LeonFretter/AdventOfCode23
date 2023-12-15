# ord(char) gets ascii value of char

def decode(s: str) -> int:
    res = 0
    for c in s:
        x = ord(c)
        res += x
        res *= 17
        res = res % 256
    return res


def decodeList(ss: list[str]) -> int:
    return sum([decode(s) for s in ss])


def readList(txt: str) -> list[str]:
    return txt.strip().split(",")


if __name__ == "__main__":
    assert decode("rn=1") == 30
    assert decode("cm-") == 253
    assert decode("qp=3") == 97
