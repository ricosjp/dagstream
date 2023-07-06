from __future__ import annotations

import abc
import graphlib


class ICallableKnot(metaclass=abc.ABCMeta):
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
    def successors(self) -> set[ICallableKnot]:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def n_predecessors(self) -> int:
        raise NotImplementedError()

    @abc.abstractmethod
    def precede(self, *functions: ICallableKnot) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def succeed(self, *functions: ICallableKnot) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def prepare(self) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def run(self) -> None:
        raise NotImplementedError()


class KnotFunction(ICallableKnot):
    def __init__(self, user_function: callable) -> None:
        self._user_function = user_function
        self._from: set[ICallableKnot] = set()
        self._to: set[ICallableKnot] = set()
        self._name = f"{KnotFunction.__name__}:{id(self)}"

        self._n_predecessors: int = None

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def n_predecessors(self) -> int:
        return self._n_predecessors

    @property
    def successors(self) -> set[ICallableKnot]:
        return self._to

    @property
    def is_nested(self) -> bool:
        return False

    def prepare(self) -> None:
        self._n_predecessors = len(self._from)

    def precede(self, *functions: ICallableKnot) -> None:
        for func in functions:
            if func in self._to:
                continue            
            self._to.add(func)
            func.succeed(self)

    def succeed(self, *functions: ICallableKnot) -> None:
        for func in functions:
            if func in self._from:
                continue
            self._from.add(func)
            func.precede(self)

    def run(self, *args, **kwargs):
        return self._user_function(args)
