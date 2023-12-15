from enum import Enum
from typing import Optional
from dataclasses import dataclass

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


class Operation(Enum):
    INSERT = 1
    REMOVE = 2


@dataclass
class LensOp:
    name: str
    op: Operation
    val: int = -1

    def __eq__(self, other: "LensOp") -> bool:
        return self.name == other.name and self.op == other.op and self.val == other.val


@dataclass
class Lens:
    name: str
    val: int

    def __eq__(self, other: "Lens") -> bool:
        return self.name == other.name


def readLensOp(txt: str) -> LensOp:
    if "-" in txt:
        op = Operation.REMOVE
        idx = txt.index("-")
        lens = txt[:idx]
        return LensOp(lens, op)
    elif "=" in txt:
        op = Operation.INSERT
        idx = txt.index("=")
        lens = txt[:idx]
        val = int(txt[idx + 1:])
        return LensOp(lens, op, val)
    raise ValueError("Invalid lens")


def readLensOps(txt: str) -> list[LensOp]:
    txts = txt.strip().split(",")
    return [readLensOp(t) for t in txts]


class LensBuckets:
    def __init__(self):
        self.buckets: list[list[Lens]] = []
        for _ in range(256):
            self.buckets.append([])

    def insert(self, op: LensOp) -> None:
        lens = Lens(op.name, op.val)
        idx = decode(op.name)
        bucket = self.buckets[idx]
        try:
            elem_idx = bucket.index(lens)
            bucket[elem_idx] = lens
        except ValueError:
            bucket.append(lens)

    def remove(self, op: LensOp) -> None:
        idx = decode(op.name)
        lens = Lens(op.name, op.val)
        if lens in self.buckets[idx]:
            self.buckets[idx].remove(lens)

    def handle(self, op: LensOp) -> None:
        if op.op == Operation.INSERT:
            self.insert(op)
        elif op.op == Operation.REMOVE:
            self.remove(op)

    def calculateFocusingPower(self) -> int:
        res = 0
        for bucket_idx, bucket in enumerate(self.buckets):
            for lens_idx, lens in enumerate(bucket):
                focal_len = lens.val
                res += (1 + bucket_idx) * (1 + lens_idx) * focal_len
        return res


if __name__ == "__main__":
    assert decode("rn=1") == 30
    assert decode("cm-") == 253
    assert decode("qp=3") == 97

    assert readLensOp("rn=1") == LensOp("rn", Operation.INSERT, 1)
    assert readLensOp("cm-") == LensOp("cm", Operation.REMOVE)

    instructions = "rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7"
    ops = readLensOps(instructions)
    bucket = LensBuckets()
    for op in ops:
        bucket.handle(op)
    res = bucket.calculateFocusingPower()
    assert res == 145
