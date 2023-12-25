import os
from trajectory import count_collisions, read_trajectories, Area, Trajectory, Vec2

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'input.txt')

with open(filename) as f:
    txt = f.read()
    trajectories = read_trajectories(txt)

    min_val = 200000000000000
    max_val = 400000000000000

    area = Area(
        Vec2(min_val, min_val),
        Vec2(max_val, max_val)
    )

    num_collisions = count_collisions(trajectories, area)

    print(f"Part 1: {num_collisions}")
