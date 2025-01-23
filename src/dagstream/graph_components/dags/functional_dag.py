from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from dagstream.graph_components._interface import (
    IDrawableNode,
    IFunctionalNode,
    INodeState,
)

from .interface import IDrawableGraph


class FunctionalDag(IDrawableGraph):
    def __init__(self, name2nodes: dict[str, IFunctionalNode]) -> None:
        self._name2nodes = name2nodes
        self._n_finished: int = 0
        self._n_functions: int = len(self._name2nodes)

        self._name2state: dict[str, INodeState] = {
            node.mut_name: node.prepare() for node in name2nodes.values()
        }
        self._ready_nodes: list[IFunctionalNode] = [
            node
            for node in name2nodes.values()
            if self._name2state[node.mut_name].is_ready
        ]

        self._last_node_names: set[str] = {
            node.mut_name
            for node in name2nodes.values()
            if self._is_last_node(node)
        }

    def _is_last_node(self, node: IFunctionalNode) -> bool:
        n_successors = sum(
            [1 for edge in node.successors if edge.to_node in self._name2nodes]
        )
        return n_successors == 0

    @property
    def is_active(self) -> bool:
        """Check whether unfinished functions exist or not

        Returns
        -------
        bool
            True if not finished functions exist
        """
        return self._n_finished < self._n_functions

    def check_last(self, node: str | IFunctionalNode) -> bool:
        if isinstance(node, str):
            return node in self._last_node_names

        if isinstance(node, IFunctionalNode):
            return node.mut_name in self._last_node_names

        raise NotImplementedError()

    def check_exists(self, node: IFunctionalNode | str) -> bool:
        """Chech whether node exists in this functional dag.

        Parameters
        ----------
        node : IFunctionalNode
            functional node to search

        Returns
        -------
        bool
            True if node exists in this functional dag.
        """
        if isinstance(node, IFunctionalNode):
            return node.mut_name in self._name2nodes
        if isinstance(node, str):
            return node in self._name2nodes

        raise NotImplementedError()

    def get_drawable_nodes(self) -> Iterable[IDrawableNode]:
        return self._name2nodes.values()

    def get_ready(self) -> tuple[IFunctionalNode, ...]:
        result = tuple(self._ready_nodes)
        self._ready_nodes.clear()
        return result

    def send(self, node_name: str, result: Any) -> None:  # noqa: ANN401
        node = self._name2nodes[node_name]

        for edge in node.successors:
            if not edge.is_pipe:
                continue

            if not self.check_exists(edge.to_node):
                continue

            next_node = self._name2nodes[edge.to_node]
            next_node.receive_args(result)

    def done(self, *node_names: str) -> None:
        """Register nodes as finished and update state

        Parameters
        ----------
        *finished_nodes : IFunctionalNode
            finished nodes

        """
        for name in node_names:
            self._n_finished += 1
            finished_node = self._name2nodes[name]
            for edge in finished_node.successors:
                if not self.check_exists(edge.to_node):
                    continue

                self._name2state[edge.to_node].forward()
                if self._name2state[edge.to_node].is_ready:
                    self._ready_nodes.append(self._name2nodes[edge.to_node])
