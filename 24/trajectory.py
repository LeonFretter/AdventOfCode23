from dataclasses import dataclass
from math import sqrt
from numpy import cross, dot
from numpy.linalg import norm


@dataclass
class Vec2:
    x: float
    y: float

    @staticmethod
    def from_vec3(v: 'Vec3'):
        return Vec2(v.x, v.y)

    def magnitude(self) -> float:
        return sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self) -> "Vec2":
        return Vec2(self.x / self.magnitude(), self.y / self.magnitude())

    def __mul__(self, other: float) -> "Vec2":
        return Vec2(self.x * other, self.y * other)

    def __div__(self, other: float) -> "Vec2":
        return Vec2(self.x / other, self.y / other)

    def __str__(self) -> str:
        return f"Vec2({self.x}, {self.y})"


@dataclass
class Vec3:
    x: float
    y: float
    z: float

    def magnitude(self) -> float:
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalize(self) -> "Vec3":
        return Vec3(self.x / self.magnitude(), self.y / self.magnitude(), self.z / self.magnitude())

    def __mul__(self, other: float) -> "Vec3":
        return Vec3(self.x * other, self.y * other, self.z * other)

    def __div__(self, other: float) -> "Vec3":
        return Vec3(self.x / other, self.y / other, self.z / other)

    def __add__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __getitem__(self, item: int) -> float:
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        elif item == 2:
            return self.z
        else:
            raise Exception("Invalid index")

    def dot(self, other: "Vec3") -> float:
        res = dot([self.x, self.y, self.z], [other.x, other.y, other.z])
        return res


@dataclass
class Line2Coord:
    # y = mx + b
    m: float
    b: float

    def get_collision_pos(self, other: "Line2Coord") -> Vec2:
        if self.m == other.m:
            raise Exception("Lines are parallel")

        x = (other.b - self.b) / (self.m - other.m)
        y = self.m * x + self.b
        return Vec2(x, y)


@dataclass
class Line2:
    start: Vec2
    direction: Vec2

    def get_coordinate_form(self) -> Line2Coord:
        # y = mx + b
        # m = dy / dx
        # b = y - mx
        m = self.direction.y / self.direction.x
        b = self.start.y - m * self.start.x
        return Line2Coord(m, b)


@dataclass
class Line3:
    start: Vec3
    direction: Vec3

    def closest_approach_to(self, other: "Line3") -> tuple[Vec3, Vec3]:
        # Calculate the unit direction vectors of the lines
        d1 = self.direction.normalize()
        d2 = other.direction.normalize()

        # Calculate the vector between the start points of the lines
        w0 = self.start - other.start

        # Calculate the parameters at the point of closest approach
        a = d1.dot(d1)
        b = d1.dot(d2)
        c = d2.dot(d2)
        d = d1.dot(w0)
        e = d2.dot(w0)
        denominator = a * c - b * b

        if denominator != 0:
            sc = (b * e - c * d) / denominator
            tc = (a * e - b * d) / denominator
        else:
            # The lines are parallel so choose an arbitrary t value
            sc = 0.0
            tc = d / b if b > a else e / c

        # Calculate the points on each line at the point of closest approach
        point_on_self = self.start + d1 * sc
        point_on_self = Vec3(point_on_self[0], point_on_self[1], point_on_self[2])
        point_on_other = other.start + d2 * tc
        point_on_other = Vec3(point_on_other[0], point_on_other[1], point_on_other[2])

        return point_on_self, point_on_other


@dataclass
class Trajectory:
    p: Vec3
    v: Vec3

    def run(self) -> "Trajectory":
        new_trajectory = Trajectory(
            Vec3(self.p.x + self.v.x, self.p.y + self.v.y, self.p.z + self.v.z),
            self.v
        )
        return new_trajectory

    def get_line2(self) -> Line2:
        return Line2(
            Vec2(self.p.x, self.p.y),
            Vec2(self.v.x, self.v.y).normalize()
        )

    def get_2d_intersection(self, other: "Trajectory") -> Vec2:
        line1 = self.get_line2()
        line2 = other.get_line2()
        pos = line1.get_coordinate_form().get_collision_pos(line2.get_coordinate_form())
        t1 = (pos.x - self.p.x) / self.v.x
        t2 = (pos.x - other.p.x) / other.v.x
        if t1 < 0 or t2 < 0:
            raise Exception("Intersect is in the past")
        return pos

    def get_3d_intersection(self, other: "Trajectory") -> Vec3:
        line1 = Line3(self.p, self.v)
        line2 = Line3(other.p, other.v)
        pos1, pos2 = line1.closest_approach_to(line2)

        tolerance = 0.001
        if (pos1 - pos2).magnitude() > tolerance:
            raise Exception("Lines do not intersect")

        t1 = (pos1.x - self.p.x) / self.v.x
        t2 = (pos1.x - other.p.x) / other.v.x
        if t1 < 0 or t2 < 0:
            raise Exception("Intersect is in the past")
        return pos1

    def __str__(self) -> str:
        return f"(p={self.p}, v={self.v})"


def read_trajectory(line: str) -> Trajectory:
    pos, vel = line.split(" @ ")
    pos = Vec3(*[float(x) for x in pos.split(",")])
    vel = Vec3(*[float(x) for x in vel.split(",")])
    return Trajectory(pos, vel)


def read_trajectories(txt: str) -> list[Trajectory]:
    return [read_trajectory(line) for line in txt.splitlines()]


@dataclass
class Area:
    min_pos: Vec2
    max_pos: Vec2

    def contains(self, pos: Vec2) -> bool:
        return self.min_pos.x <= pos.x <= self.max_pos.x and self.min_pos.y <= pos.y <= self.max_pos.y


def count_collisions(trajectories: list[Trajectory], area: Area) -> int:
    collisions = 0
    for i in range(len(trajectories)):
        for j in range(i + 1, len(trajectories)):
            try:
                traj_a = trajectories[i]
                traj_b = trajectories[j]
                intersection = traj_a.get_2d_intersection(traj_b)
                if area.contains(intersection):
                    collisions += 1
            except Exception:
                pass
    return collisions


def count_3d_collisions(traj_a: Trajectory, trajectories: list[Trajectory]) -> int:
    collisions = 0
    for i in range(len(trajectories)):
        try:
            traj_b = trajectories[i]
            intersection = traj_a.get_3d_intersection(traj_b)
            collisions += 1
        except Exception:
            pass
    return collisions


if __name__ == "__main__":
    txt = str("""\
19, 13, 30 @ -2,  1, -2
18, 19, 22 @ -1, -1, -2
20, 25, 34 @ -2, -2, -4
12, 31, 28 @ -1, -2, -1
20, 19, 15 @  1, -5, -3
""")

    area = Area(Vec2(7, 7), Vec2(27, 27))
    trajectories = read_trajectories(txt)
    for i in range(len(trajectories)):
        for j in range(i + 1, len(trajectories)):
            try:
                traj_a = trajectories[i]
                traj_b = trajectories[j]
                intersection = traj_a.get_2d_intersection(traj_b)
                if area.contains(intersection):
                    print(f"Trajectory {traj_a} and {traj_b} intersect at {intersection}")
            except Exception:
                pass
    assert count_collisions(trajectories, area) == 2

    rock_traj = Trajectory(Vec3(24, 13, 10), Vec3(-3, 1, 2))

    for i in range(len(trajectories)):
        try:
            traj = trajectories[i]
            intersection = rock_traj.get_3d_intersection(traj)
            print(f"Trajectory {traj} intersects rock at {intersection}")
        except Exception:
            pass
