from typing import Iterable

from dagstream.graph_components.nodes import IDrawableNode, IFunctionalNode
from .interface import IDrawableGraph


class FunctionalDag(IDrawableGraph):
    def __init__(self, nodes: set[IFunctionalNode]) -> None:
        self.nodes = nodes
        self._n_finished: int = 0
        self._n_functions: int = len(self.nodes)
        self._ready_nodes: list[IFunctionalNode] = [
            node for node in self.nodes if node.n_predecessors == 0
        ]

    @property
    def is_active(self) -> bool:
        if self._ready_nodes is None:
            raise ValueError("prepare() must be called first")

        return self._n_finished < self._n_functions

    def is_exist_node(self, node: IFunctionalNode) -> bool:
        return node in self.nodes

    def get_drawable_nodes(self) -> Iterable[IDrawableNode]:
        return self.nodes

    def get_ready(self) -> tuple[IFunctionalNode, ...]:
        result = tuple(self._ready_nodes)
        self._ready_nodes.clear()
        return result

    def done(self, *finished_nodes: IFunctionalNode) -> None:
        for node in finished_nodes:
            self._n_finished += 1
            for successor in node.successors:
                if successor not in self.nodes:
                    # If it is sub dag graph, it is possible
                    # that successor does not exists
                    continue

                successor.state.forward()
                if successor.state.is_ready:
                    self._ready_nodes.append(successor)
