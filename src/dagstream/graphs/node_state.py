import abc


class INodeState(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def n_predecessors(self) -> int:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def is_ready(self) -> bool:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def is_finished(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def forward(self) -> None:
        raise NotImplementedError()


class NodeState(INodeState):
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
