from __future__ import annotations

import types
from typing import Any, Callable, Iterable

from dagstream.graph_components.edges import DagEdge
from dagstream.graph_components._interface import IDagEdge, IFunctionalNode, IDrawableNode

from .node_state import ReadyNodeState


# NOTE: If FunctionalNode has reference to other nodes, 
# one node has almost all information of DAG.
# It costs too much memory and it is difficult to multi-processing.
# So, a node has only names about connected ones.


class FunctionalNode(IFunctionalNode, IDrawableNode):
    def __init__(self, user_function: Callable) -> None:
        self._user_function = user_function
        self._from: set[str] = set()
        self._to_edges: dict[str, IDagEdge] = {}
        self._mut_name = self._get_name(user_function)
        self._display_name =  self._get_name(user_function)

        self.__received: list[Any] = []

    def _get_name(self, user_function: Callable) -> str:
        if isinstance(user_function, types.FunctionType):
            return user_function.__name__

        return user_function.__class__.__name__

    def __repr__(self) -> str:
        return f"{FunctionalNode.__name__}: {self._display_name}"

    def __hash__(self):
        return hash(self.mut_name)

    @property
    def display_name(self) -> str:
        return self._display_name

    @display_name.setter
    def display_name(self, value: str):
        self._display_name = value

    @property
    def mut_name(self) -> str:
        return self._mut_name

    @property
    def n_predecessors(self) -> int:
        return len(self._from)

    @property
    def n_successors(self) -> int:
        return len(self._to_edges)

    @property
    def predecessors(self) -> set[str]:
        return self._from

    @property
    def successors(self) -> list[IDagEdge]:
        return self._to_edges.values()

    @property
    def forward_edges(self) -> dict[str, IDagEdge]:
        return self._to_edges.values()

    def prepare(self) -> ReadyNodeState:
        self.__received = []
        return ReadyNodeState(self.n_predecessors)

    def receive_args(self, val: Any) -> None:
        self.__received.append(val)

    def precede(self, *nodes: FunctionalNode, pipe: bool = False) -> None:
        for node in nodes:
            if node._mut_name in self._to_edges:
                continue

            self._to_edges[node._mut_name] = DagEdge(
                from_node=self.mut_name,
                to_node=node.mut_name,
                pipe=pipe
            )
            node.succeed(self, pipe=pipe)

    def succeed(self, *nodes: FunctionalNode, pipe: bool = False) -> None:
        for node in nodes:
            if node in self._from:
                continue
            self._from.add(node.mut_name)
            node.precede(self, pipe=pipe)

    def run(self, *args, **kwargs):
        result = self._user_function(*self.__received, *args, **kwargs)        
        return result
