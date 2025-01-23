import pytest

from dagstream.graph_components.edges import DagEdge


@pytest.mark.parametrize(
    "from_node, to_node, is_pipe",
    [("node1", "node2", True), ("node1", "node2", False)],
)
def test__is_pipe(from_node: str, to_node: str, is_pipe: bool):
    edge = DagEdge(from_node, to_node, is_pipe)

    assert edge.is_pipe == is_pipe


@pytest.mark.parametrize(
    "from_node, to_node, is_pipe",
    [("node1", "node22", True), ("node11", "node32", False)],
)
def test__to_node(from_node: str, to_node: str, is_pipe: bool):
    edge = DagEdge(from_node, to_node, is_pipe)

    assert edge.to_node == to_node
