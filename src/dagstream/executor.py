from dagstream.graph_components import FunctionalDag


class StreamExecutor:
    def __init__(self, functional_dag: FunctionalDag) -> None:
        self._dag = functional_dag

    def run(self, *args, **kwargs) -> None:
        while self._dag.is_active:
            nodes = self._dag.get_ready()
            for node in nodes:
                node.run(*args, **kwargs)
                self._dag.done(node)
