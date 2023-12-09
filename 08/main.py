import os
from tree import ProblemSet, Traversal, InstructionCircle, spawnMultiTraversal
from sys import argv
from part2 import Waypoint, WaypointManager
from dataclasses import dataclass

dirname = os.path.dirname(__file__)
inputfile = os.path.join(dirname, "input.txt")
args = argv[1:]


@dataclass
class Part2Traversal:
    waypoint: Waypoint
    instruction_count: int = 0

with open(inputfile) as f:
    lines = f.readlines()

    problem = ProblemSet(lines)

    start_node = problem.graph.getNode("AAA")
    end_node = problem.graph.getNode("ZZZ")

    traversal = Traversal(problem.graph, InstructionCircle(problem.instructions), start_node)
    while traversal.current != end_node:
        traversal.next()

    print(f"Part 1: {traversal.steps()}")

    waypoint_manager = WaypointManager(problem.instructions, problem.graph.nodes)
    waypoints = waypoint_manager.waypoints

    start_nodes = [node for node in problem.graph.nodes if node.name[2] == "A"]
    it_waypoints = [waypoints[0][problem.graph.nodes.index(node)] for node in start_nodes]
    print("start_waypoints", it_waypoints)

    traversals: list[Part2Traversal] = [Part2Traversal(waypoint) for waypoint in it_waypoints]

    found = False
    i = 0
    while not found:
        if all([t.waypoint.distance == 0 for t in traversals]):
            if len(set([t.instruction_count for t in traversals])) == len(traversals):
                print(f"Part 2: {traversals[0].instruction_count}")
                found = True
                break
            else:
                traversals = sorted(traversals, key=lambda t: t.instruction_count)
                traversal = traversals[0]
                next_child = traversal.waypoint.child
                next_wp = next_child.next_destination
                dist = 1 + next_child.distance
                traversal.instruction_count += dist

                i += 1
                if i % 1000 == 0:
                    print(f"min-count: {traversals[0].instruction_count}")
