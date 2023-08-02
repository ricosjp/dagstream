import abc
from typing import Iterable

from dagstream.graph_components.nodes import IDrawableNode, IFunctionalNode


class IDrawableGraph(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_drawable_nodes(self) -> Iterable[IDrawableNode]:
        raise NotImplementedError()

    @abc.abstractmethod
    def check_exists(self, node: IFunctionalNode) -> bool:
        raise NotImplementedError()
