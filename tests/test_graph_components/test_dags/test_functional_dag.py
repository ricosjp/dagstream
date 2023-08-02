from unittest import mock
import pytest

from dagstream.graph_components import FunctionalDag
from dagstream.graph_components.nodes import FunctionalNode


@pytest.fixture
def create_functional_nodes() -> list[FunctionalNode]:
    def sample1(): pass
    def sample2(): pass
    def sample3(): pass

    node1 = FunctionalNode(sample1)
    node2 = FunctionalNode(sample2)
    node3 = FunctionalNode(sample3)

    """
    Relationship

    node1 --> node2 --> node3
      |                   ^
      --------------------|
    """
    node1.precede(node2, node3)
    node3.succeed(node2)
    return [node1, node2, node3]


def test__initialized(create_functional_nodes):
    with mock.patch.object(FunctionalNode, "prepare") as mocked:
        dag = FunctionalDag(create_functional_nodes)

        assert mocked.call_count == len(create_functional_nodes)


def test__n_finished_when_initialized(create_functional_nodes: list[FunctionalNode]):
    dag = FunctionalDag(create_functional_nodes)
    assert dag._n_finished == 0


def test__get_ready(create_functional_nodes: list[FunctionalNode]):
    dag = FunctionalDag(create_functional_nodes)

    result = dag.get_ready()
    assert len(result) == 1

    node = result[0]
    assert node.name == "sample1"


def test__get_ready_nodes(create_functional_nodes: list[FunctionalNode]):
    dag = FunctionalDag(create_functional_nodes)

    result = dag.get_ready()
    dag.done(*result)

    next_nodes = dag.get_ready()
    assert len(next_nodes) == 1
    assert next_nodes[0].name == "sample2"
    dag.done(*next_nodes)

    next_nodes = dag.get_ready()
    assert len(next_nodes) == 1
    assert next_nodes[0].name == "sample3"


def test__n_finished_when_done():
    def sample(): pass
    dag = FunctionalDag([FunctionalNode(sample)])

    node, = dag.get_ready()

    dag.done(node)
    assert dag._n_finished == 1

