import dataclasses
from collections.abc import (
    Collection,
    Iterable,
    Iterator,
    Mapping,
)
from typing import final

type Graph[L] = Mapping[L, Collection[L]]


@final
@dataclasses.dataclass
class _Node[L]:
    label: L
    root: int = -2  # -2 (not visited), -1 (lowlink), or int >= 0
    succ: list["_Node[L]"] = dataclasses.field(default_factory=list)


def _from_graph[L](graph: Graph[L]) -> Iterable[_Node[L]]:
    nodes = dict()
    for v, ps in graph.items():
        for w in ps:
            if v not in nodes:
                nodes[v] = _Node(v)
            if w not in nodes:
                nodes[w] = _Node(w)
            nodes[v].succ.append(nodes[w])

    return nodes.values()


def _strongconnect[L](node: _Node[L], stack: list[_Node[L]]) -> Iterator[frozenset[L]]:
    node.root = pos = len(stack)
    stack.append(node)

    for w in node.succ:
        if w.root == -2:  # not yet visited
            yield from _strongconnect(w, stack)

        if w.root >= 0:  # still on stack
            node.root = min(node.root, w.root)

    if node.root == pos:  # v is the root, return everything above
        res, stack[pos:] = stack[pos:], []
        for w in res:
            w.root = -1
        yield frozenset(r.label for r in res)


def strongly_connected_components[L](graph: Graph[L]) -> Iterator[frozenset[L]]:
    for v in _from_graph(graph):
        if v.root == -2:
            yield from _strongconnect(v, [])
