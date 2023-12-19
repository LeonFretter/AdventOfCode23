from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Optional
from itertools import combinations


class Operator(Enum):
    LESS_THAN = "<"
    GREATER_THAN = ">"


@dataclass
class Condition:
    var_name: str
    operator: Operator
    value: int

    def __call__(self, elements: "Elements") -> bool:
        value = getattr(elements, self.var_name)
        if self.operator == Operator.LESS_THAN:
            return value < self.value
        elif self.operator == Operator.GREATER_THAN:
            return value > self.value
        else:
            raise RuntimeError("Unknown operator")

    def __str__(self) -> str:
        return f"{self.var_name}{self.operator.value}{self.value}"

    def invert(self) -> "Condition":
        if self.operator == Operator.LESS_THAN:
            return Condition(self.var_name, Operator.GREATER_THAN, self.value - 1)
        elif self.operator == Operator.GREATER_THAN:
            return Condition(self.var_name, Operator.LESS_THAN, self.value + 1)
        else:
            raise RuntimeError("Unknown operator")


@dataclass
class Rule:
    target: str
    condition: Optional[Condition] = None

    def __str__(self) -> str:
        if self.condition is None:
            return self.target
        return f"{self.condition}:{self.target}"


def parseRule(rule_txt: str) -> Rule:
    if ":" not in rule_txt:
        return Rule(rule_txt)

    condition_txt, target_txt = rule_txt.split(":")
    var_name = ""
    operator = Operator.LESS_THAN
    value = 0

    for i in range(len(condition_txt)):
        c = condition_txt[i]
        if c.isalpha():
            var_name += c
        elif c == "<":
            operator = Operator.LESS_THAN
        elif c == ">":
            operator = Operator.GREATER_THAN
        else:
            value = int(condition_txt[i:])
            break
    condition = Condition(var_name, operator, value)
    return Rule(target_txt, condition)


@dataclass
class Workflow:
    name: str
    rules: list[Rule]

    def __call__(self, elements: "Elements") -> str:
        for rule in self.rules:
            if rule.condition is None:
                return rule.target
            if rule.condition(elements):
                return rule.target
        raise RuntimeError("No rule matched")


def readWorkflow(line: str) -> Workflow:
    name, rules_txt = line.split("{")
    rules_txt = rules_txt[:-1]
    rules_txts = rules_txt.split(",")
    rules = [parseRule(rule_txt) for rule_txt in rules_txts]
    return Workflow(name, rules)


@dataclass
class Elements:
    x: int
    m: int
    a: int
    s: int

    def __int__(self) -> int:
        return self.x + self.m + self.a + self.s


def readElements(line: str) -> Elements:
    inner = line.strip("{").strip("}")
    elems_txt = inner.split(",")
    x = 0
    m = 0
    a = 0
    s = 0
    for elem_txt in elems_txt:
        elem_name, elem_value = elem_txt.split("=")
        value = int(elem_value)
        if elem_name == "x":
            x = value
        elif elem_name == "m":
            m = value
        elif elem_name == "a":
            a = value
        elif elem_name == "s":
            s = value
    return Elements(x, m, a, s)


@dataclass
class ProblemSet:
    workflows: list[Workflow]
    elements: list[Elements]

    def __call__(self) -> list[Elements]:
        accepted: list[Elements] = []
        for elems in self.elements:
            workflow = next(w for w in self.workflows if w.name == "in")
            result = self.runWorkflow(workflow, elems)
            if result is not None:
                accepted.append(result)
        return accepted

    def runWorkflow(self, workflow: Workflow, elems: Elements) -> Optional[Elements]:
        target = workflow(elems)
        if target == "A":
            return elems
        elif target == "R":
            return None
        else:
            workflow = next(w for w in self.workflows if w.name == target)
            return self.runWorkflow(workflow, elems)


def readProblemSet(input_txt: str) -> ProblemSet:
    lines = input_txt.splitlines()
    workflows: list[Workflow] = []
    elements: list[Elements] = []
    i = 0
    line = lines[i]
    while line != "":
        workflow = readWorkflow(line)
        workflows.append(workflow)
        i += 1
        line = lines[i]

    for j in range(i + 1, len(lines)):
        line = lines[j]
        elems = readElements(line)
        elements.append(elems)

    return ProblemSet(workflows, elements)


@dataclass
class WorkflowNode:
    workflow: Workflow | str
    children: list["WorkflowTree"] = field(default_factory=list)
    parent: Optional["WorkflowNode"] = None

    def getLeaves(self) -> "list[WorkflowNode]":
        leaves: list[WorkflowNode] = []
        if isinstance(self.workflow, str):
            return [self]
        for child in self.children:
            leaves.extend(child.getLeaves())
        return leaves

    def getPaths(self) -> "list[WorkflowPath]":
        paths: list[list[WorkflowNode]] = []
        leaves = self.getLeaves()
        for leaf in leaves:
            path: list[WorkflowNode] = []
            node = leaf
            while node is not None:
                path.append(node)
                node = node.parent
            paths.append(list(reversed(path)))
        return paths


type WorkflowTree = WorkflowNode
type WorkflowPath = list[WorkflowNode]


def buildWorkflowNode(node: WorkflowTree, workflows: list[Workflow]) -> None:
    if isinstance(node.workflow, str):
        return
    workflow = node.workflow
    children: list[WorkflowTree] = []
    for rule in workflow.rules:
        target = rule.target
        if target == "A" or target == "R":
            child_node = WorkflowNode(target)
            child_node.parent = node
            children.append(child_node)
        else:
            child = next(w for w in workflows if w.name == target)
            child_node = WorkflowNode(child)
            child_node.parent = node
            buildWorkflowNode(child_node, workflows)
            children.append(child_node)
        node.children = children


def buildWorkflowTree(workflows: list[Workflow]) -> WorkflowNode:
    root = next(w for w in workflows if w.name == "in")
    node = WorkflowNode(root)
    buildWorkflowNode(node, workflows)
    return node


def filterPaths(paths: list[WorkflowPath]) -> list[WorkflowPath]:
    res: list[WorkflowPath] = []
    for p in paths:
        leave = p[-1]
        if leave.workflow == "A":
            res.append(p)
    return res


def getConditions(path: WorkflowPath) -> list[Condition]:
    """
        None is interpreted as tautology
    """
    res: list[Condition] = []
    for i in range(len(path) - 1):
        node = path[i]
        next_node = path[i + 1]
        if isinstance(node.workflow, Workflow):
            next_name = ""
            if isinstance(next_node.workflow, str):
                next_name = next_node.workflow
            else:
                next_name = next_node.workflow.name

            condition = None
            prev_conditions = []
            for r in node.workflow.rules:
                if r.target == next_name:
                    condition = r.condition
                else:
                    prev_conditions.append(r.condition)
            prev_inverted = [c.invert() for c in prev_conditions if c is not None]
            res.extend(prev_inverted)
            if condition is not None:
                res.append(condition)
    return res


@dataclass
class Conjunction:
    conditions: list[Condition]

    def __str__(self) -> str:
        return " and ".join(str(c) if c is not None else "*" for c in self.conditions)

    def get_min_val(self, var_name: str) -> int:
        x = 1
        for c in self.conditions:
            if c.var_name == var_name and c.operator == Operator.GREATER_THAN:
                x = max(x, c.value + 1)
        return x

    def get_max_val(self, var_name: str) -> int:
        x = 4000
        for c in self.conditions:
            if c.var_name == var_name and c.operator == Operator.LESS_THAN:
                x = min(x, c.value - 1)
        return x


class Range:
    def __init__(self, var_name: str = "", conj: Conjunction | None = None) -> None:
        if var_name != "" and conj is not None:
            self.min_val = conj.get_min_val(var_name)
            self.max_val = conj.get_max_val(var_name)

    def count(self) -> int:
        if self.min_val > self.max_val:
            return 0
        return self.max_val - self.min_val + 1

    def copy(self) -> "Range":
        new_range = Range()
        new_range.min_val = self.min_val
        new_range.max_val = self.max_val
        return new_range

    @staticmethod
    def intersection(a: "Range", b: "Range") -> "Range":
        res = Range()
        res.min_val = max(a.min_val, b.min_val)
        res.max_val = min(a.max_val, b.max_val)
        return res

    @staticmethod
    def union(a: "Range", b: "Range") -> "Range":
        """
            Assumes that there's no gap between a and b
        """
        res = Range()
        res.min_val = min(a.min_val, b.min_val)
        res.max_val = max(a.max_val, b.max_val)
        return res

    @staticmethod
    def get_unique(elems: "list[Range]") -> "list[Range]":
        unions: list[Range] = elems
        while True:
            if len(unions) == 1:
                break

            next_unions = []
            considered: list[Range] = []
            for i in range(0, len(unions)):
                for j in range():
                    pass

            for i in range(0, len(unions), 2):
                if i + 1 == len(unions):
                    next_unions.append(unions[i])
                    break
                a = unions[i]
                b = unions[i + 1]
                intersection = Range.intersection(a, b)
                if intersection.count() > 0:
                    union = Range.union(a, b)
                    next_unions.append(union)
                else:
                    next_unions.append(a)
                    next_unions.append(b)
            if sum(u.count() for u in next_unions) == sum(u.count() for u in unions):
                break
            unions = next_unions
        return unions


class RangeSet:
    def __init__(self, conj: Conjunction) -> None:
        self.x = Range("x", conj)
        self.m = Range("m", conj)
        self.a = Range("a", conj)
        self.s = Range("s", conj)


class RangeSetDisjunction:
    def __init__(self, conjunctions: list[Conjunction]) -> None:
        self.range_sets = [RangeSet(c) for c in conjunctions]

    def count(self) -> int:
        xs = [r.x for r in self.range_sets]
        ms = [r.m for r in self.range_sets]
        as_ = [r.a for r in self.range_sets]
        ss = [r.s for r in self.range_sets]

        xs = Range.get_unique(xs)
        ms = Range.get_unique(ms)
        as_ = Range.get_unique(as_)
        ss = Range.get_unique(ss)

        x = sum(r.count() for r in xs)
        m = sum(r.count() for r in ms)
        a = sum(r.count() for r in as_)
        s = sum(r.count() for r in ss)

        return x * m * a * s


if __name__ == "__main__":
    txt = """\
px{a<2006:qkq,m>2090:A,rfg}
pv{a>1716:R,A}
lnx{m>1548:A,A}
rfg{s<537:gd,x>2440:R,A}
qs{s>3448:A,lnx}
qkq{x<1416:A,crn}
crn{x>2662:A,R}
in{s<1351:px,qqz}
qqz{s>2770:qs,m<1801:hdj,R}
gd{a>3333:R,R}
hdj{m>838:A,pv}

{x=787,m=2655,a=1222,s=2876}
{x=1679,m=44,a=2067,s=496}
{x=2036,m=264,a=79,s=2244}
{x=2461,m=1339,a=466,s=291}
{x=2127,m=1623,a=2188,s=1013}\
"""
    problem_set = readProblemSet(txt)

    assert len(problem_set.workflows) == 11
    assert len(problem_set.elements) == 5

    accepted = problem_set()

    res = sum(int(e) for e in accepted)
    assert res == 19114

    tree = buildWorkflowTree(problem_set.workflows)
    paths = tree.getPaths()
    print("path-count: " + str(len(paths)))
    paths = filterPaths(paths)
    print("filtered path-count: " + str(len(paths)))
    conjunctions = [Conjunction(getConditions(p)) for p in paths]
    print("conjunctions:")
    for c in conjunctions:
        print(c)

    range_set_disjunction = RangeSetDisjunction(conjunctions)

    count = range_set_disjunction.count()
    assert count == 167409079868000
