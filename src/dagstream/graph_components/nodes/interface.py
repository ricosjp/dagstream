from __future__ import annotations

import abc
from typing import Any

from .node_state import INodeState


class IDrawableNode(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def successors(self) -> set[IFunctionalNode]:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def n_predecessors(self) -> int:
        raise NotImplementedError()


class IFunctionalNode(IDrawableNode, metaclass=abc.ABCMeta):
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
    def predecessors(self) -> set[IFunctionalNode]:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def successors(self) -> set[IFunctionalNode]:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def n_predecessors(self) -> int:
        raise NotImplementedError()

    @abc.abstractmethod
    def precede(self, *functions: IFunctionalNode) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def succeed(self, *functions: IFunctionalNode) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def prepare(self) -> INodeState:
        raise NotImplementedError()

    @abc.abstractmethod
    def run(self, *args, **kwargs) -> Any:
        raise NotImplementedError()
