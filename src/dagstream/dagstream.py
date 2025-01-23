from __future__ import annotations

from collections.abc import Callable, Iterable

from dagstream import utils
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
        # This counter aims to distinguish
        # between nodes which have the same function name
        self._SAME_NAME_COUNTER: dict[str, int] = {}

    def check_exists(self, node: str | IFunctionalNode) -> bool:
        if isinstance(node, IFunctionalNode):
            return node.mut_name in self._name2node

        if isinstance(node, str):
            return node in self._name2node

        raise NotImplementedError()

    def get_drawable_nodes(self) -> Iterable[IDrawableNode]:
        return self._name2node.values()

    def get_functions(self) -> Iterable[IFunctionalNode]:
        return self._name2node.values()

    def emplace(self, *functions: Callable) -> tuple[IFunctionalNode, ...]:
        """create a functional node corresponding to each function

        Returns
        -------
        tuple[IFunctionalNode, ...]
            functional node corresponding to each function
        """

        # To ensure orders
        _nodes: list[IFunctionalNode] = []
        for func in functions:
            node_name = self._create_node_name(func)
            node = FunctionalNode(func, mut_node_name=node_name)
            _nodes.append(node)
            self._name2node.update({node.mut_name: node})

        return tuple(_nodes)

    def _create_node_name(self, user_function: Callable) -> str:
        function_name = utils.get_function_name(user_function)
        if function_name not in self._name2node:
            return function_name

        _counter = self._SAME_NAME_COUNTER.get(function_name, 0)
        _counter += 1

        node_name = f"{function_name}_{_counter}"

        self._SAME_NAME_COUNTER[function_name] = _counter
        return node_name

    def construct(
        self, mandatory_nodes: set[IFunctionalNode] | None = None
    ) -> FunctionalDag:
        """create functional dag

        Solving dependencies and create dag structure composed
          of functional nodes

        Parameters
        ----------
        mandatory_nodes : Optional[set[IFunctionalNode]], optional
            If fed, extract sub 'minimum' graph to include mandatory_nodes.
            If not fed, all functional nodes are included to graph.
              by default None

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
        self,
        mandatory_node: IFunctionalNode,
        visited: dict[str, IFunctionalNode],
    ):
        if mandatory_node.mut_name in visited:
            return

        visited.update({mandatory_node.mut_name: mandatory_node})
        predecessors: list[str] = list(mandatory_node.predecessors)

        while len(predecessors) != 0:
            node_name = predecessors.pop()
            node = self._name2node[node_name]
            if node.mut_name in visited:
                continue
            visited.update({node.mut_name: node})

            for next_node in node.predecessors:
                predecessors.append(next_node)

        return None

    def _detect_cycle(self):
        finished: set[str] = set()
        seen: set[str] = set()
        for node in self._name2node.values():
            if node.mut_name in finished:
                continue
            self._dfs_detect_cycle(node, finished, seen)
        return None

    def _dfs_detect_cycle(
        self,
        start: IFunctionalNode,
        finished: set[str],
        seen: set[str],
    ) -> None:
        for edge in start.successors:
            node = self._name2node[edge.to_node]

            if node.mut_name in finished:
                continue

            if (node.mut_name in seen) and (node.mut_name not in finished):
                raise DagStreamCycleError(
                    "Detect cycle in your definition of dag."
                )

            seen.add(node.mut_name)
            self._dfs_detect_cycle(node, finished, seen)

        finished.add(start.mut_name)
