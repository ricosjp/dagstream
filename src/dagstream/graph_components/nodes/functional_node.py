from __future__ import annotations
from typing import Callable

from .interface import IFunctionalNode, IDrawableNode
from .node_state import INodeState, ReadyNodeState, UnReadyNodeState


class FunctionalNode(IFunctionalNode, IDrawableNode):
    def __init__(self, user_function: Callable) -> None:
        self._user_function = user_function
        self._from: set[IFunctionalNode] = set()
        self._to: set[IFunctionalNode] = set()
        self._name = f"{user_function.__name__}"
        self._state: INodeState = UnReadyNodeState()

    def __repr__(self) -> str:
        return f"{FunctionalNode.__name__}:{self.name}"

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def n_predecessors(self) -> int:
        return len(self._from)

    @property
    def state(self) -> INodeState:
        return self._state

    @property
    def predecessors(self) -> set[IFunctionalNode]:
        return self._from

    @property
    def successors(self) -> set[IFunctionalNode]:
        return self._to

    def prepare(self) -> None:
        self._state = ReadyNodeState(self.n_predecessors)

    def precede(self, *functions: IFunctionalNode) -> None:
        for func in functions:
            if func in self._to:
                continue
            self._to.add(func)
            func.succeed(self)

    def succeed(self, *functions: IFunctionalNode) -> None:
        for func in functions:
            if func in self._from:
                continue
            self._from.add(func)
            func.precede(self)

    def run(self, *args, **kwargs):
        return self._user_function()