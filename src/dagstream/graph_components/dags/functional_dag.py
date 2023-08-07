from typing import Iterable

from dagstream.graph_components.nodes import IDrawableNode, IFunctionalNode, INodeState

from .interface import IDrawableGraph


class FunctionalDag(IDrawableGraph):
    def __init__(self, nodes: set[IFunctionalNode]) -> None:
        self._nodes = nodes
        self._n_finished: int = 0
        self._n_functions: int = len(self._nodes)

        self._name2state: dict[IFunctionalNode, INodeState] = {
            node: node.prepare() for node in self._nodes
        }
        self._ready_nodes: list[IFunctionalNode] = [
            node for node in self._nodes if self._name2state[node].is_ready
        ]

    @property
    def is_active(self) -> bool:
        """Check whether unfinished functions exist or not

        Returns
        -------
        bool
            True if not finished functions exist
        """
        return self._n_finished < self._n_functions

    def check_exists(self, node: IFunctionalNode) -> bool:
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
        return node in self._nodes

    def get_drawable_nodes(self) -> Iterable[IDrawableNode]:
        return self._nodes

    def get_ready(self) -> tuple[IFunctionalNode, ...]:
        result = tuple(self._ready_nodes)
        self._ready_nodes.clear()
        return result

    def done(self, *finished_nodes: IFunctionalNode) -> None:
        """Register nodes as finished and update state

        Parameters
        ----------
        *finished_nodes : IFunctionalNode
            finished nodes

        """
        for node in finished_nodes:
            self._n_finished += 1
            for successor in node.successors:
                if successor not in self._nodes:
                    # If it is last node,
                    # successor does not exists
                    continue

                self._name2state[successor].forward()
                if self._name2state[successor].is_ready:
                    self._ready_nodes.append(successor)
