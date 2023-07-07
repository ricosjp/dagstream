
from dagstream.graph_components import FunctionalDag


class StreamExecutor:
    def __init__(self) -> None:
        ...

    def run(sel, functional_dag: FunctionalDag) -> None:
        while functional_dag.is_active:
            nodes = functional_dag.get_ready()
            for node in nodes:
                node.run()
                functional_dag.done(node)
