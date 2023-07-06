import abc

from collections import deque
from typing import Iterable

from dagstream.knot_function import ICallableKnot, KnotFunction


class DagStream:
    def __init__(self) -> None:
        self._functions: set[ICallableKnot] = set()
        self._ready_nodes: set[ICallableKnot] = None

        self._n_functions: int = 0
        self._n_finished: int = 0

    @property
    def is_active(self) -> bool:
        if self._ready_nodes is None:
            raise ValueError("prepare() must be called first")

        return self._n_finished < self._n_functions

    def emplace(self, *functions: callable) -> tuple[KnotFunction]:
        knot_functions = {KnotFunction(func) for func in functions}
        for func in knot_functions:
            self._functions.add(func)
        return knot_functions

    def get_ready(self) -> Iterable[ICallableKnot]:
        if self._ready_nodes is None:
            raise ValueError("prepare() must be called first")

        return self._ready_nodes

    def prepare(self) -> None:
        self._detect_cycle()

        for func in self._functions:
            func.prepare()

        self._n_functions = len(self._functions)
        self._ready_nodes = {
            node for node in self._functions
            if node.n_predecessors == 0
        }

    def done(self, *functions: KnotFunction) -> None:
        for func in functions:
            self._n_finished += 1
            self._ready_nodes.remove(func)
            for successor in func.successors:
                successor.n_predecessors -= 1
                if(successor.n_predecessors == 0):
                    self._ready_nodes.add(successor)

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
        start: ICallableKnot, 
        finished: set[ICallableKnot], 
        seen: set[ICallableKnot]
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
