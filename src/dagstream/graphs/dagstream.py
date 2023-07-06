import pathlib
from typing import Iterable

from dagstream.graphs.functional_node import FunctionalNode, IFunctionalNode
from dagstream.viewers import IViewer


class DagFunctionalGraph:
    def __init__(self, nodes: Iterable[IFunctionalNode]) -> None:
        self.nodes = nodes
        self._ready_nodes: set[IFunctionalNode] = None
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

    def output(self, viewer: IViewer, file_path: pathlib.Path) -> None:
        viewer.output(self.nodes, file_path=file_path)

    def get_ready(self) -> tuple[IFunctionalNode]:
        result = tuple(self._ready_nodes)
        self._ready_nodes.clear()
        return result

    def done(self, *finished_nodes: IFunctionalNode) -> None:
        for node in finished_nodes:
            self._n_finished += 1
            for successor in node.successors:
                successor.state.forward()
                if successor.state.is_ready:
                    self._ready_nodes.append(successor)


class DagStream:
    def __init__(self) -> None:
        self._functions: set[IFunctionalNode] = set()

    def get_functions(self) -> set[IFunctionalNode]:
        return self._functions

    def emplace(self, *functions: callable) -> tuple[FunctionalNode, ...]:
        knot_functions = tuple([FunctionalNode(func) for func in functions])
        for func in knot_functions:
            self._functions.add(func)
        return knot_functions

    def output(self, viewer: IViewer, file_path: pathlib.Path) -> None:
        viewer.output(self._functions, file_path=file_path)

    def construct(self) -> DagFunctionalGraph:
        self._detect_cycle()
        for func in self._functions:
            func.prepare()
        # TODO: Add extract feature
        return DagFunctionalGraph(self._functions)

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
                raise DagStreamCycleError()

            seen.add(node)
            self._dfs_detect_cycle(node, finished, seen)

        finished.add(start)


class DagStreamCycleError(ValueError):
    pass
