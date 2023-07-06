
from dagstream.dagstream import DagStream


class StreamExecutor:
    def __init__(self, dag_stream: DagStream) -> None:
        self._dag_stream = dag_stream

    def run(self, n_cpus: int = 1) -> None:
        self._dag_stream.prepare()

