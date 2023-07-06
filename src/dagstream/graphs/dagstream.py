import pathlib
from typing import Callable, Iterable

from dagstream.graphs.functional_dag import DagFunctionalGraph
from dagstream.graphs.functional_node import FunctionalNode, IFunctionalNode
from dagstream.viewers import IViewer


class DagStream:
    def __init__(self) -> None:
        self._functions: set[IFunctionalNode] = set()

    def get_functions(self) -> set[IFunctionalNode]:
        return self._functions

    def emplace(self, *functions: Callable) -> tuple[FunctionalNode, ...]:
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
        return DagFunctionalGraph(set(self._functions))

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
