import abc
from typing import Iterable, Union

from dagstream.graph_components._interface import IDrawableNode, IFunctionalNode


class IDrawableGraph(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_drawable_nodes(self) -> Iterable[IDrawableNode]:
        raise NotImplementedError()

    @abc.abstractmethod
    def check_exists(self, node: Union[IFunctionalNode, str]) -> bool:
        raise NotImplementedError()
