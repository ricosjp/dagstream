import abc
import pathlib
from typing import Iterable

from dagstream.graphs.interface import IDrawableGraph
from dagstream.graphs.nodes import IDrawableNode


class IDrawer(metaclass=abc.ABCMeta):
    def output(
        self, functions: Iterable[IDrawableNode], file_path: pathlib.Path
    ) -> None:
        raise NotImplementedError()


class MermaidDrawer(IDrawer):
    def __init__(self) -> None:
        pass

    def output(
        self, graph: IDrawableGraph, file_path: pathlib.Path
    ) -> None:
        context = self._generate(graph)
        with open(file_path, "w") as fw:
            fw.write(context)

    def _generate(self, graph: IDrawableGraph) -> str:
        context = ["stateDiagram"]
        name2id = {}

        nodes = graph.get_drawable_nodes()
        for i, node in enumerate(nodes):
            name2id[node.name] = (state_name := f"state_{i}")
            context.append(f'state "{node.name}" as {state_name}')

        for i, node in enumerate(nodes):
            state_name = name2id[node.name]
            if node.n_predecessors == 0:
                context.append(f"[*] --> {state_name}")

            if len(node.successors) == 0:
                context.append(f"{state_name} --> [*]")
                continue

            for successor in node.successors:
                successor_state = name2id[successor.name]
                context.append(f"{state_name} --> {successor_state}")

        spliter = "\n" + " " * 4
        return spliter.join(context)
