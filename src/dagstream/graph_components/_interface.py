from __future__ import annotations

import abc
from typing import Any, Iterable, Union


class IDrawableNode(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def display_name(self) -> str:
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
    def display_name(self) -> str:
        ...

    @display_name.setter
    @abc.abstractmethod
    def display_name(self) -> None:
        ...

    @property
    @abc.abstractmethod
    def mut_name(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def predecessors(self) -> set[str]:
        ...

    @property
    @abc.abstractmethod
    def successors(self) -> Iterable[IDagEdge]:
        ...

    @property
    @abc.abstractmethod
    def n_predecessors(self) -> int:
        ...

    @property
    @abc.abstractmethod
    def n_successors(self) -> int:
        ...

    @property
    @abc.abstractmethod
    def forward_edges(self) -> Iterable[IDagEdge]:
        ...

    @abc.abstractmethod
    def precede(self, *functions: IFunctionalNode) -> None:
        ...

    @abc.abstractmethod
    def succeed(self, *functions: IFunctionalNode) -> None:
        ...

    @abc.abstractmethod
    def prepare(self) -> INodeState:
        ...

    @abc.abstractmethod
    def receive_args(self, *val: Union[Any, None]) -> None:
        ...

    @abc.abstractmethod
    def run(self, *args, **kwargs) -> Any:
        ...


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
    def is_pipe(self) -> bool:
        ...

    @property
    @abc.abstractmethod
    def to_node(self) -> str:
        ...
