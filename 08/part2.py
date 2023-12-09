from tree import Node, step, Graph
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Waypoint:
    node: Node
    child: Optional["Waypoint"] = None
    distance: int = -1
    next_destination: Optional["Waypoint"] = None


class WaypointManager:
    def __init__(self, instructions: str, nodes: list[Node]):
        self.instructions = instructions
        self.nodes = nodes
        self.graph = Graph(nodes)
        self.waypoints: list[list[Waypoint]] = []

        for _ in range(len(instructions)):
            self.waypoints.append([Waypoint(node) for node in self.nodes])

        for i in range(len(instructions)):
            for j in range(len(self.nodes)):
                child_node = step(self.graph, self.waypoints[i][j].node, instructions[i])
                self.waypoints[i][j].child = self.waypoints[(i + 1) % len(self.instructions)][self.nodes.index(child_node)]

        set_waypoint_distances = 0
        while set_waypoint_distances < len(instructions * len(nodes)):
            print(f"set_waypoint_distances: {set_waypoint_distances} of {len(instructions) * len(nodes)}")
            for i in range(len(instructions)):
                for j in range(len(self.nodes)):
                    wp = self.waypoints[i][j]
                    if wp.distance == -1:
                        if wp.node.name[2] == "Z":
                            wp.distance = 0
                            set_waypoint_distances += 1
                            wp.next_destination = wp
                        elif wp.child.distance != -1:
                            wp.distance = wp.child.distance + 1
                            set_waypoint_distances += 1
                            wp.next_destination = wp.child.next_destination
