import abc
import pathlib
from typing import Iterable

from dagstream.graphs.functional_node import IFunctionalNode


class IViewer(metaclass=abc.ABCMeta):
    def output(
        self, functions: Iterable[IFunctionalNode], file_path: pathlib.Path
    ) -> None:
        raise NotImplementedError()


class MermaidViewer(IViewer):
    def __init__(self) -> None:
        pass

    def output(
        self, functions: Iterable[IFunctionalNode], file_path: pathlib.Path
    ) -> None:
        context = self._generate(functions)
        with open(file_path, "w") as fw:
            fw.write(context)

    def _generate(self, functions: Iterable[IFunctionalNode]) -> str:
        context = ["stateDiagram"]
        name2id = {}

        for i, node in enumerate(functions):
            name2id[node.name] = (state_name := f"state_{i}")
            context.append(f'state "{node.name}" as {state_name}')

        for i, node in enumerate(functions):
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
