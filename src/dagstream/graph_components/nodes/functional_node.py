from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from dagstream import utils
from dagstream.graph_components._interface import (
    IDagEdge,
    IDrawableNode,
    IFunctionalNode,
)
from dagstream.graph_components.edges import DagEdge
from dagstream.graph_components.nodes.node_state import ReadyNodeState

# NOTE: If FunctionalNode has reference to other nodes,
# one node has almost all information of DAG.
# It costs too much memory and it is difficult to multi-processing.
# So, a node has only names about connected ones.


class FunctionalNode(IFunctionalNode, IDrawableNode):
    def __init__(
        self,
        user_function: Callable[[Any], Any],
        *,
        mut_node_name: str | None = None,
    ) -> None:
        self._user_function = user_function
        self._from: set[str] = set()
        self._to_edges: dict[str, IDagEdge] = {}

        if mut_node_name is None:
            mut_node_name = utils.get_function_name(user_function)
        self._mut_name = mut_node_name
        self._display_name = utils.get_function_name(user_function)

        self.__received: list[Any] = []

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
    def successors(self) -> Iterable[IDagEdge]:
        return self._to_edges.values()

    def prepare(self) -> ReadyNodeState:
        self.__received = []
        return ReadyNodeState(self.n_predecessors)

    def receive_args(self, val: Any) -> None:  # noqa: ANN401
        self.__received.append(val)

    def get_user_function(self) -> Callable[[Any], Any]:
        return self._user_function

    def get_received_args(self) -> list[Any]:
        return self.__received

    def precede(self, *nodes: IFunctionalNode, pipe: bool = False) -> None:
        for node in nodes:
            if node.mut_name in self._to_edges:
                continue

            self._to_edges[node.mut_name] = DagEdge(
                from_node=self.mut_name, to_node=node.mut_name, pipe=pipe
            )
            node.succeed(self, pipe=pipe)

    def succeed(self, *nodes: IFunctionalNode, pipe: bool = False) -> None:
        for node in nodes:
            if node.mut_name in self._from:
                continue
            self._from.add(node.mut_name)
            node.precede(self, pipe=pipe)

    def run(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        result = self._user_function(*self.__received, *args, **kwargs)
        return result
