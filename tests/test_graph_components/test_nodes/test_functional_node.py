from unittest import mock

import pytest

from dagstream.graph_components.nodes import FunctionalNode, node_state


def test__get_function_name():
    def sample():
        pass

    node = FunctionalNode(sample)
    assert node.display_name == "sample"


def test__get_callable_class_name():
    class SampleClass:
        def __init__(self) -> None:
            pass

        def __call__(self):
            pass

    node = FunctionalNode(SampleClass())
    assert node.display_name == "SampleClass"


def test__change_function_name():
    def sample():
        pass

    node = FunctionalNode(sample)
    node.display_name = "sample2"
    assert node.display_name == "sample2"


def test__call_succeed_when_precede():
    def sample1():
        pass

    def sample2():
        pass

    node1 = FunctionalNode(sample1)
    node2 = FunctionalNode(sample2)

    with mock.patch.object(FunctionalNode, "succeed") as mocked:
        node1.precede(node2)
        mocked.assert_called_once()


def test__call_precede_when_succeed():
    def sample1():
        pass

    def sample2():
        pass

    node1 = FunctionalNode(sample1)
    node2 = FunctionalNode(sample2)

    with mock.patch.object(FunctionalNode, "precede") as mocked:
        node1.succeed(node2)
        mocked.assert_called_once()


@pytest.fixture
def create_nodes_relationship():
    def sample1():
        pass

    def sample2():
        pass

    def sample3():
        pass

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
    return node1, node2, node3


def test__precede_succeed_relationship(
    create_nodes_relationship: tuple[FunctionalNode, ...]
):
    node1, node2, node3 = create_nodes_relationship

    assert node1.n_predecessors == 0
    assert node2.n_predecessors == 1
    assert node3.n_predecessors == 2

    assert len(node1.successors) == 2
    assert len(node2.successors) == 1
    assert len(node3.successors) == 0


def test_prepare():
    def sample1():
        pass

    node1 = FunctionalNode(sample1)
    state = node1.prepare()
    assert isinstance(state, node_state.ReadyNodeState)


def test__n_successors(create_nodes_relationship: tuple[FunctionalNode, ...]):
    node1, node2, node3 = create_nodes_relationship

    assert node1.n_successors == 2
    assert node2.n_successors == 1
    assert node3.n_successors == 0


def test__hash(create_nodes_relationship):
    node1, node2, node3 = create_nodes_relationship

    assert hash(node1) == hash(node1)
    assert hash(node1) != hash(node2)
    assert hash(node1) != hash(node3)


def test__user_function():
    def sample1():
        pass

    def sample2():
        pass

    node1 = FunctionalNode(sample1)
    node2 = FunctionalNode(sample2)

    assert node1.get_user_function() == sample1
    assert node2.get_user_function() == sample2


@pytest.mark.parametrize(
    "args", [("sample", 3, [2, 3, 4]), (2, 3, 4), ({"a": 2}, 4, (3, 4))]
)
def test__get_received_args(args):
    def sample1():
        ...

    node1 = FunctionalNode(sample1)
    for arg in args:
        node1.receive_args(arg)

    assert node1.get_received_args() == list(args)
