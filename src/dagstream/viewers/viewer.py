from __future__ import annotations

import abc
import pathlib

from dagstream.graph_components import IDrawableGraph


class IDrawer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def output(self, graph: IDrawableGraph, file_path: pathlib.Path) -> None:
        raise NotImplementedError()


class MermaidDrawer(IDrawer):
    def __init__(self) -> None:
        self._spliter = "\n" + " " * 4
        self._dir = "LR"

    def output(
        self, graph: IDrawableGraph, file_path: pathlib.Path | str
    ) -> None:
        """output content to file_path

        Parameters
        ----------
        graph : IDrawableGraph
            graph object to draw
        file_path : pathlib.Path
            path to file
        """
        context = self._generate(graph)
        with open(file_path, "w") as fw:
            fw.write(context)

    def _generate(self, graph: IDrawableGraph) -> str:
        context = ["stateDiagram", f"direction {self._dir}"]
        name2id: dict[str, str] = {}

        nodes = graph.get_drawable_nodes()
        for i, node in enumerate(nodes):
            name2id[node.mut_name] = (state_name := f"state_{i}")
            context.append(f'state "{node.display_name}" as {state_name}')

        for _, node in enumerate(nodes):
            state_name = name2id[node.mut_name]
            if node.n_predecessors == 0:
                context.append(f"[*] --> {state_name}")

            succesors = [
                v for v in node.successors if graph.check_exists(v.to_node)
            ]
            if len(succesors) == 0:
                context.append(f"{state_name} --> [*]")
                continue

            for successor in succesors:
                successor_state = name2id[successor.to_node]
                if successor.is_pipe:
                    context.append(f"{state_name} --> {successor_state}: Pipe")
                else:
                    context.append(f"{state_name} --> {successor_state}")

        return self._spliter.join(context)
