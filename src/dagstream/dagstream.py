from typing import Callable, Iterable, Optional

from dagstream.graph_components import (
    FunctionalDag,
    IDrawableGraph,
    IDrawableNode,
    IFunctionalNode,
)
from dagstream.graph_components.nodes import FunctionalNode
from dagstream.utils.errors import DagStreamCycleError


class DagStream(IDrawableGraph):
    def __init__(self) -> None:
        self._name2node: dict[str, IFunctionalNode] = {}

    def check_exists(self, node: IFunctionalNode) -> bool:
        return node.mut_name in self._name2node

    def get_drawable_nodes(self) -> Iterable[IDrawableNode]:
        return self._name2node.values()

    def get_functions(self) -> set[IFunctionalNode]:
        return self._name2node.values()

    def emplace(self, *functions: Callable) -> tuple[IFunctionalNode, ...]:
        """create a functional node corresponding to each function

        Returns
        -------
        tuple[IFunctionalNode, ...]
            functional node corresponding to each function
        """

        # To ensure orders
        _functions: dict[str, IFunctionalNode] = {}
        for func in functions:
            node = FunctionalNode(func)
            _functions.update({node.mut_name: node})

        self._name2node |= _functions
        return tuple(_functions.values())

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
            functions = self._name2node
        else:
            functions = self._extract_functions(mandatory_nodes)

        return FunctionalDag(functions)

    def _extract_functions(
        self, mandatory_nodes: set[IFunctionalNode]
    ) -> dict[str, IFunctionalNode]:
        visited: dict[str, IFunctionalNode] = {}

        for node in mandatory_nodes:
            self._extract_subdag(node, visited)
        return visited

    def _extract_subdag(
        self, mandatory_node: IFunctionalNode, visited: dict[str, IFunctionalNode]
    ):
        if mandatory_node.mut_name in visited:
            return

        visited.update({mandatory_node.mut_name: mandatory_node})
        predecessors: list[str] = [v for v in mandatory_node.predecessors]

        while len(predecessors) != 0:
            node_name = predecessors.pop()
            node = self._name2node[node_name]
            if node in visited:
                continue
            visited.update({node.mut_name: node})

            for next_node in node.predecessors:
                predecessors.append(next_node)

        return None

    def _detect_cycle(self):
        finished = set()
        seen = set()
        for node in self._name2node.values():
            if node in finished:
                continue
            self._dfs_detect_cycle(node, finished, seen)
        return None

    def _dfs_detect_cycle(
        self,
        start: IFunctionalNode,
        finished: set[IFunctionalNode],
        seen: set[IFunctionalNode],
    ) -> None:
        for edge in start.successors:
            node = self._name2node[edge.to_node]

            if node in finished:
                continue

            if (node in seen) and (node not in finished):
                raise DagStreamCycleError("Detect cycle in your definition of dag.")

            seen.add(node)
            self._dfs_detect_cycle(node, finished, seen)

        finished.add(start)
