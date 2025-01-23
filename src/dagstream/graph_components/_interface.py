from __future__ import annotations

import abc
from collections.abc import Iterable
from typing import Any


class IDrawableNode(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def display_name(self) -> str: ...

    @property
    @abc.abstractmethod
    def mut_name(self) -> str: ...

    @property
    @abc.abstractmethod
    def successors(self) -> Iterable[IDagEdge]: ...

    @property
    @abc.abstractmethod
    def n_predecessors(self) -> int: ...


class IFunctionalNode(IDrawableNode, metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def display_name(self) -> str: ...

    @display_name.setter
    @abc.abstractmethod
    def display_name(self) -> None: ...

    @property
    @abc.abstractmethod
    def mut_name(self) -> str: ...

    @property
    @abc.abstractmethod
    def predecessors(self) -> set[str]: ...

    @property
    @abc.abstractmethod
    def successors(self) -> Iterable[IDagEdge]: ...

    @property
    @abc.abstractmethod
    def n_predecessors(self) -> int: ...

    @property
    @abc.abstractmethod
    def n_successors(self) -> int: ...

    @abc.abstractmethod
    def precede(self, *nodes: IFunctionalNode, pipe: bool = False) -> None: ...

    @abc.abstractmethod
    def succeed(self, *nodes: IFunctionalNode, pipe: bool = False) -> None: ...

    @abc.abstractmethod
    def prepare(self) -> INodeState: ...

    @abc.abstractmethod
    def receive_args(self, val: Any) -> None: ...  # noqa: ANN401

    @abc.abstractmethod
    def get_received_args(self) -> list[Any]: ...

    @abc.abstractmethod
    def get_user_function(self) -> Any: ...  # noqa: ANN401

    @abc.abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any: ...  # noqa: ANN401


class INodeState(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def n_predecessors(self) -> int:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def is_ready(self) -> bool:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def is_finished(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def forward(self) -> None:
        raise NotImplementedError()


class IDagEdge(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def is_pipe(self) -> bool: ...

    @property
    @abc.abstractmethod
    def to_node(self) -> str: ...
