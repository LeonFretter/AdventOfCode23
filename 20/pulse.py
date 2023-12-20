from dataclasses import dataclass, field
from typing import override


@dataclass
class NodeBlueprint:
    name: str
    children: list[str]
    node_type: str


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

    @property
    def node_type(self) -> str:
        return self.blueprint.node_type

    def updateConfig(self) -> None:
        pass

    def receive(self, pulse: bool, origin: "Node") -> "list[tuple[Node, Node, bool]]":
        if pulse:
            self.high_pulse_count += 1
        else:
            self.low_pulse_count += 1
        return []

    def conditionStr(self) -> str:
        return "_"

    def pathsTo(self) -> "list[list[Node]]":
        paths: list[list[Node]] = [[self]]
        while not all([path[-1].parents == [] for path in paths]):
            new_paths = []
            for p in paths:
                parents = p[-1].parents
                if p[-1].parents == []:
                    new_paths.append(p)
                for par in parents:
                    if par in p:
                        dummy = LoopDummyNode(NodeBlueprint("dummy", [], "dummy"))
                        dummy.original = par
                        new_paths.append(p + [dummy])
                    else:
                        new_paths.append(p + [par])
            paths = new_paths
        return [list(reversed(path)) for path in paths]

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        res = self.name
        if self.node_type in ["%", "&"]:
            res += self.node_type
        if self.node_type == "&":
            res += str(len(self.parents))
        return res


@dataclass
class LoopDummyNode(Node):
    original: Node | None = None

    @override
    def conditionStr(self) -> str:
        return "(loop:" + self.original.conditionStr() + ")"


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

    @override
    def conditionStr(self) -> str:
        names = [p.name for p in self.parents]
        names = [name + "=0" for name in names]
        return "(" + " | ".join(names) + " -> !" + self.name + ".state)"

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

    @override
    def conditionStr(self) -> str:
        return "(" + " & ".join([p.name for p in self.parents]) + ")"

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

    @override
    def conditionStr(self) -> str:
        return "(*)"

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
    blueprint = NodeBlueprint(node_name, children, node_type)

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
    nodes = readNodes(lines)
    nodes["rx"] = Node(NodeBlueprint("rx", [], "rx"), [], [])

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
    button = Node(NodeBlueprint("button", [], "btn"), [], [])

    @property
    def broadcaster(self) -> Broadcaster:
        res = self.nodes["broadcaster"]
        assert isinstance(res, Broadcaster)
        return res

    @property
    def rx(self) -> Node:
        return self.nodes["rx"]

    def pressButton(self) -> None:
        stack: list[tuple[Node, Node, bool]] = [(self.button, self.broadcaster, False)]
        while stack:
            src, dst, pulse = stack.pop()
            stack.extend(dst.receive(pulse, src))

    def pressButtonMulti(self, times: int) -> None:
        for _ in range(times):
            self.pressButton()

    def pressButtonUntil(self) -> int:
        i = 0
        while not self.rx.low_pulse_count:
            self.pressButton()
            i += 1
            if i % 1000 == 0:
                print(i)
        return i

    def countPulses(self) -> int:
        low_pulse_count = 0
        high_pulse_count = 0
        for node in self.nodes.values():
            low_pulse_count += node.low_pulse_count
            high_pulse_count += node.high_pulse_count
        return low_pulse_count * high_pulse_count

    def conditionStrPath(self, path: list[Node]) -> str:
        return " -> ".join([node.conditionStr() for node in path])

    def conditionStr(self, target: str) -> list[str]:
        node = self.nodes[target]
        paths = node.pathsTo()
        return [self.conditionStrPath(path) for path in paths]

    def pathStr(self, target: str) -> list[str]:
        node = self.nodes[target]
        paths = node.pathsTo()
        res = []
        for p in paths:
            res.append("[" + ", ".join([str(node) for node in p]) + "]")
        return res


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

    cc2 = CommandCenter(connectNodes(example_lines))
    condition_str = cc2.conditionStr("a")

    print("\n".join(condition_str))