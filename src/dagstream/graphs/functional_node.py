from __future__ import annotations

import abc
from typing import Callable, Union

from .node_state import INodeState, ReadyNodeState, UnReadyNodeState


class IFunctionalNode(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError()

    @name.setter
    @abc.abstractmethod
    def name(self) -> None:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def successors(self) -> set[IFunctionalNode]:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def n_predecessors(self) -> int:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def state(self) -> INodeState:
        raise NotImplementedError()

    @abc.abstractmethod
    def precede(self, *functions: IFunctionalNode) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def succeed(self, *functions: IFunctionalNode) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def prepare(self) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def run(self) -> None:
        raise NotImplementedError()


class FunctionalNode(IFunctionalNode):
    def __init__(self, user_function: Callable) -> None:
        self._user_function = user_function
        self._from: set[IFunctionalNode] = set()
        self._to: set[IFunctionalNode] = set()
        self._name = f"{user_function.__name__}"

        self._state: INodeState = UnReadyNodeState()

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
