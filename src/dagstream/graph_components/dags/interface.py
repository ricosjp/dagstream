from __future__ import annotations

import abc
from collections.abc import Iterable

from dagstream.graph_components._interface import IDrawableNode, IFunctionalNode


class IDrawableGraph(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_drawable_nodes(self) -> Iterable[IDrawableNode]:
        raise NotImplementedError()

    @abc.abstractmethod
    def check_exists(self, node: IFunctionalNode | str) -> bool:
        raise NotImplementedError()
