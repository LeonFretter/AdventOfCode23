from dataclasses import dataclass, field
from typing import override


@dataclass
class NodeBlueprint:
    name: str
    children: list[str]


@dataclass
class Node:
    blueprint: NodeBlueprint
    children: "list[Node]" = field(default_factory=list)
    parents: "list[Node]" = field(default_factory=list)
    low_pulse_count = 0
    high_pulse_count = 0

    @property
    def name(self) -> str:
        return self.blueprint.name

    def updateConfig(self) -> None:
        pass

    def receive(self, pulse: bool, origin: "Node") -> "list[tuple[Node, Node, bool]]":
        if pulse:
            self.high_pulse_count += 1
        else:
            self.low_pulse_count += 1
        return []

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class FlipFlop(Node):
    state: bool = False

    @override
    def receive(self, pulse: bool, origin: Node) -> list[tuple[Node, Node, bool]]:
        super().receive(pulse, origin)
        res: list[tuple[Node, Node, bool]] = []
        if not pulse:
            self.state = not self.state
            for child in self.children:
                res.append((self, child, self.state))
        return res

    def __bool__(self) -> bool:
        return self.state

    def __hash__(self) -> int:
        return super().__hash__()


@dataclass
class Conjunction(Node):
    inputs: dict[Node, bool] = field(default_factory=dict)

    @override
    def updateConfig(self) -> None:
        for parent in self.parents:
            self.inputs[parent] = False

    @override
    def receive(self, pulse: bool, origin: Node) -> list[tuple[Node, Node, bool]]:
        super().receive(pulse, origin)
        self.inputs[origin] = pulse
        out_pulse = not all(self.inputs.values())
        res: list[tuple[Node, Node, bool]] = []
        for child in self.children:
            res.append((self, child, out_pulse))
        return res

    def __hash__(self) -> int:
        return super().__hash__()


@dataclass
class Broadcaster(Node):
    def receive(self, pulse: bool, origin: Node):
        super().receive(pulse, origin)
        res: list[tuple[Node, Node, bool]] = []
        for child in self.children:
            res.append((self, child, pulse))
        return res

    def __hash__(self) -> int:
        return super().__hash__()


def readNode(line: str) -> Node:
    node_txt, children_txt = line.split(" -> ")
    if node_txt == "broadcaster":
        node_type = node_txt
        node_name = node_txt
    else:
        node_type = node_txt[0]
        node_name = node_txt[1:]

    children = children_txt.split(", ")
    blueprint = NodeBlueprint(node_name, children)

    node = {
        "%": FlipFlop(blueprint),
        "&": Conjunction(blueprint),
        "broadcaster": Broadcaster(blueprint),
    }[node_type]

    return node


def readNodes(lines: list[str]) -> dict[str, Node]:
    nodes = {}
    for line in lines:
        node = readNode(line)
        nodes[node.name] = node
    return nodes


def connectNodes(lines: list[str]) -> dict[str, Node]:
    old_nodes = readNodes(lines)
    nodes = old_nodes.copy()

    for node in old_nodes.values():
        for child_name in node.blueprint.children:
            if child_name not in nodes:
                child = Node(NodeBlueprint(child_name, []), [], [])
                nodes[child_name] = child

    for node in nodes.values():
        for child_name in node.blueprint.children:
            child = nodes[child_name]
            node.children.append(child)
            child.parents.append(node)

    for node in nodes.values():
        node.updateConfig()

    return nodes


@dataclass
class CommandCenter:
    nodes: dict[str, Node]
    button = Node(NodeBlueprint("button", []), [], [])

    @property
    def broadcaster(self) -> Broadcaster:
        res = self.nodes["broadcaster"]
        assert isinstance(res, Broadcaster)
        return res

    def pressButton(self) -> None:
        stack: list[tuple[Node, Node, bool]] = [(self.button, self.broadcaster, False)]
        while stack:
            src, dst, pulse = stack.pop()
            stack.extend(dst.receive(pulse, src))

    def pressButtonMulti(self, times: int) -> None:
        for _ in range(times):
            self.pressButton()

    def countPulses(self) -> int:
        low_pulse_count = 0
        high_pulse_count = 0
        for node in self.nodes.values():
            low_pulse_count += node.low_pulse_count
            high_pulse_count += node.high_pulse_count
        return low_pulse_count * high_pulse_count


if __name__ == "__main__":
    example_txt: str = str("""\
broadcaster -> a, b, c
%a -> b
%b -> c
%c -> inv
&inv -> a\
""")
    example_lines: list[str] = example_txt.splitlines()
    example_nodes = connectNodes(example_lines)

    example_cc = CommandCenter(example_nodes)
    example_cc.pressButtonMulti(1000)
    num_pulses = example_cc.countPulses()
    assert num_pulses == 32000000
