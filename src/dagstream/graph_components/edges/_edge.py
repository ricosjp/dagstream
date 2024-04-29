from dagstream.graph_components._interface import IDagEdge


class DagEdge(IDagEdge):
    def __init__(self, from_node: str, to_node: str, pipe: bool) -> None:
        self._from = from_node
        self._to = to_node
        self._pipe = pipe

    @property
    def is_pipe(self) -> bool:
        return self._pipe

    @property
    def to_node(self) -> str:
        return self._to
