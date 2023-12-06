from dataclasses import dataclass


def calculateDistance(time: int, charge: int) -> int:
    return (time - charge) * charge


@dataclass
class Race:
    time: int
    distance: int

    def countWinners(self) -> int:
        count = 0
        for charge in range(1, self.time):
            if calculateDistance(self.time, charge) > self.distance:
                count += 1
        return count


def readRaces(lines: list[str]) -> list[Race]:
    times_txt = lines[0].split("Time:")[1].strip().split(" ")
    times = [int(time.strip()) for time in times_txt if time.strip() != ""]
    distances_txt = lines[1].split("Distance:")[1].strip().split(" ")
    distances = [int(distance.strip()) for distance in distances_txt if distance.strip() != ""]

    races: list[Race] = []
    for i in range(0, len(times)):
        races.append(Race(times[i], distances[i]))
    return races


def joinRaces(races: list[Race]) -> Race:
    res_time = ""
    res_dist = ""
    for r in races:
        res_time += str(r.time)
        res_dist += str(r.distance)

    return Race(int(res_time), int(res_dist))


if __name__ == "__main__":
    exampleRace = Race(4, 3)
    assert calculateDistance(4, 1) == 3
    assert calculateDistance(4, 2) == 4
    assert calculateDistance(4, 3) == 3
    assert calculateDistance(4, 4) == 0

    assert exampleRace.countWinners() == 1

    exampleRace2 = Race(6, 5)

    joined = joinRaces([exampleRace, exampleRace2])
    assert joined.time == 46
    assert joined.distance == 35
