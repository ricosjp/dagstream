from typing import Callable, Iterable, Optional

from dagstream.graph_components import FunctionalDag, IDrawableGraph
from dagstream.graph_components.nodes import (
    FunctionalNode,
    IDrawableNode,
    IFunctionalNode,
)
from dagstream.utils.errors import DagStreamCycleError


class DagStream(IDrawableGraph):
    def __init__(self) -> None:
        self._functions: set[IFunctionalNode] = set()

    def check_exists(self, node: IFunctionalNode) -> bool:
        return node in self._functions

    def get_drawable_nodes(self) -> Iterable[IDrawableNode]:
        return self._functions

    def get_functions(self) -> set[IFunctionalNode]:
        return self._functions

    def emplace(self, *functions: Callable) -> tuple[IFunctionalNode, ...]:
        """create a functional node corresponding to each function

        Returns
        -------
        tuple[IFunctionalNode, ...]
            functional node corresponding to each function
        """

        # To ensure orders
        _functions: list[IFunctionalNode] = []
        for func in functions:
            node = FunctionalNode(func)
            _functions.append(node)
            self._functions.add(node)
        return tuple(_functions)

    def construct(
        self, mandatory_nodes: Optional[set[IFunctionalNode]] = None
    ) -> FunctionalDag:
        """create functional dag

        Solving dependencies and create dag structure composed of functional nodes

        Parameters
        ----------
        mandatory_nodes : Optional[set[IFunctionalNode]], optional
            If fed, extract sub 'minimum' graph to include mandatory_nodes.
            If not fed, all functional nodes are included to graph. by default None

        Returns
        -------
        FunctionalDag
            dag structure object composed of functional nodes
        """
        self._detect_cycle()

        if mandatory_nodes is None:
            functions = self._functions
        else:
            functions = self._extract_functions(mandatory_nodes)

        return FunctionalDag(functions)

    def _extract_functions(
        self, mandatory_nodes: set[IFunctionalNode]
    ) -> set[IFunctionalNode]:
        visited: set[IFunctionalNode] = set()

        for node in mandatory_nodes:
            self._extract_subdag(node, visited)
        return visited

    def _extract_subdag(
        self, mandatory_node: IFunctionalNode, visited: set[IFunctionalNode]
    ):
        if mandatory_node in visited:
            return

        visited.add(mandatory_node)
        predecessors: list[IFunctionalNode] = [v for v in mandatory_node.predecessors]

        while len(predecessors) != 0:
            node = predecessors.pop()
            if node in visited:
                continue
            visited.add(node)

            for next_node in node.predecessors:
                predecessors.append(next_node)

        return None

    def _detect_cycle(self):
        finished = set()
        seen = set()
        for func in self._functions:
            if func in finished:
                continue
            self._dfs_detect_cycle(func, finished, seen)
        return None

    def _dfs_detect_cycle(
        self,
        start: IFunctionalNode,
        finished: set[IFunctionalNode],
        seen: set[IFunctionalNode],
    ) -> None:
        for node in start.successors:
            if node in finished:
                continue

            if (node in seen) and (node not in finished):
                raise DagStreamCycleError("Detect cycle in your definition of dag.")

            seen.add(node)
            self._dfs_detect_cycle(node, finished, seen)

        finished.add(start)
