from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Optional


class Operator(Enum):
    LESS_THAN = 1
    GREATER_THAN = 2


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


@dataclass
class Rule:
    target: str
    condition: Optional[Condition] = None


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

    def getPaths(self) -> "list[list[WorkflowNode]]":
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

    buildWorkflowTree(problem_set.workflows)
