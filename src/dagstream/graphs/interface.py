import abc
from typing import Iterable

from .nodes import IDrawableNode


class IDrawableGraph(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_drawable_nodes(self) -> Iterable[IDrawableNode]:
        raise NotImplementedError()
