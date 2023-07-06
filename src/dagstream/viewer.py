from dagstream.knot_function import ICallableKnot


class DagStreamViewer:
    def __init__(self, function: ICallableKnot) -> None:
        self._function = function

    def plot(self) -> None:
        self._function.prepare()


class MermaidViewer:
    def __init__(self, start: ICallableKnot) -> None:
        self._start = start

    def create(self) -> list[str]:
        self._start

    def convert(self) -> str:
        ...
