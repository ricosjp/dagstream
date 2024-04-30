from dagstream.graph_components._interface import INodeState
from dagstream.utils.errors import DagStreamNotReadyError


class UnReadyNodeState(INodeState):
    def __init__(self) -> None:
        pass

    @property
    def n_predecessors(self) -> int:
        raise DagStreamNotReadyError()

    @property
    def is_finished(self) -> bool:
        raise DagStreamNotReadyError()

    @property
    def is_ready(self) -> bool:
        return False

    def forward(self) -> None:
        raise DagStreamNotReadyError()


class ReadyNodeState(INodeState):
    def __init__(self, n_predecessors: int) -> None:
        self._n_predecessors = n_predecessors

    @property
    def n_predecessors(self) -> int:
        return self._n_predecessors

    @property
    def is_finished(self) -> bool:
        return self._n_predecessors < 0

    @property
    def is_ready(self) -> bool:
        return self._n_predecessors == 0

    def forward(self) -> None:
        self._n_predecessors -= 1
