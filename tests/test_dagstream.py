from unittest import mock

import pytest

from dagstream import DagStream
from dagstream.graph_components.nodes import FunctionalNode
from dagstream.utils.errors import DagStreamCycleError


def test__emplace():
    def sample1():
        pass

    def sample2():
        pass

    def sample3():
        pass

    def sample4():
        pass

    stream = DagStream()
    nodes = stream.emplace(sample1, sample2, sample3, sample4)
    assert len(nodes) == 4
    assert isinstance(nodes, tuple)

    assert nodes[0].display_name == "sample1"
    assert nodes[1].display_name == "sample2"
    assert nodes[2].display_name == "sample3"
    assert nodes[3].display_name == "sample4"


@pytest.fixture
def setup_dagstream():
    def A():
        pass

    def B():
        pass

    def C():
        pass

    def D():
        pass

    def E():
        pass

    def F():
        pass

    stream = DagStream()
    nodes = stream.emplace(A, B, C, D, E, F)

    name2node = {v.display_name: v for v in nodes}
    return stream, name2node


def setup_nodes_relationship(
    relationships: dict[str, list[str]], name2node: dict[str, FunctionalNode]
) -> None:
    for k, v in relationships.items():
        name2node[k].precede(*[name2node[name] for name in v])


@pytest.mark.parametrize(
    "relationship",
    [({"A": ["B", "C"], "B": ["E"], "C": ["E", "D"], "D": ["E"], "E": ["F"]})],
)
def test__exist_all_nodes_when_construct(
    relationship, setup_dagstream: tuple[DagStream, dict[str, FunctionalNode]]
):
    stream, name2node = setup_dagstream
    setup_nodes_relationship(relationship, name2node)
    nodes = stream.get_functions()

    dag = stream.construct()
    assert len(nodes) > 0
    for node in nodes:
        assert dag.check_exists(node)


@pytest.mark.parametrize(
    "relationship",
    [
        ({"A": ["B"], "B": ["C"], "C": ["A"]}),
        ({"A": ["B", "E"], "B": ["C"], "C": ["D"], "D": ["B", "F"]}),
        ({"A": ["B"], "B": ["C", "D"], "C": ["E"], "E": ["F"], "F": ["C"]}),
    ],
)
def test__detect_cycle(
    relationship, setup_dagstream: tuple[DagStream, dict[str, FunctionalNode]]
):
    stream, name2node = setup_dagstream
    setup_nodes_relationship(relationship, name2node)

    with pytest.raises(DagStreamCycleError):
        stream.construct()


def test__call_count_when_construct(
    setup_dagstream: tuple[DagStream, dict[str, FunctionalNode]]
):
    stream, _ = setup_dagstream

    with mock.patch.object(DagStream, "_extract_functions") as mocked:
        stream.construct()
        mocked.assert_not_called()


@pytest.mark.parametrize("mandatory_nodes", [(["A", "B"])])
def test__call_count_when_construct_with_mandatory(
    mandatory_nodes, setup_dagstream: tuple[DagStream, dict[str, FunctionalNode]]
):
    stream, _ = setup_dagstream

    with mock.patch.object(DagStream, "_extract_functions") as mocked:
        stream.construct(mandatory_nodes)
        mocked.assert_called_once()


@pytest.mark.parametrize(
    "relationship, necessary_nodes",
    [
        (
            {"A": ["B", "C"], "B": ["E"], "C": ["E", "D"], "D": ["E"], "E": ["F"]},
            ["A", "C"],
        )
    ],
)
def test__is_exist_node_when_extracting_functions(
    relationship,
    necessary_nodes,
    setup_dagstream: tuple[DagStream, dict[str, FunctionalNode]],
):
    stream, name2node = setup_dagstream
    nodes = [name2node[name] for name in necessary_nodes]
    setup_nodes_relationship(relationship, name2node)
    dag = stream.construct(nodes)

    for node in nodes:
        assert dag.check_exists(node)


@pytest.mark.parametrize(
    "relationship, necessary_nodes, contain_nodes",
    [
        (
            {"A": ["B", "C"], "B": ["E"], "C": ["E", "D"], "D": ["E"], "E": ["F"]},
            ["A"],
            ["A"],
        ),
        (
            {"A": ["B", "C"], "B": ["E"], "C": ["E", "D"], "D": ["E"], "E": ["F"]},
            ["A", "C"],
            ["A", "C"],
        ),
        (
            {"A": ["B", "C"], "B": ["E"], "C": ["E", "D"], "D": ["E"], "E": ["F"]},
            ["E"],
            ["A", "B", "C", "D", "E"],
        ),
        (
            {"A": ["B", "C"], "B": ["E"], "C": ["E", "D"], "D": ["E"], "E": ["F"]},
            ["D"],
            ["A", "C", "D"],
        ),
        (
            {"A": ["B", "C"], "B": ["E"], "C": ["E", "D"], "D": ["E"], "E": ["F"]},
            ["F"],
            ["A", "B", "C", "D", "E", "F"],
        ),
    ],
)
def test__is_subdag_graph_when_extracting(
    relationship,
    necessary_nodes,
    contain_nodes,
    setup_dagstream: tuple[DagStream, dict[str, FunctionalNode]],
):
    stream, name2node = setup_dagstream
    nodes = [name2node[name] for name in necessary_nodes]
    setup_nodes_relationship(relationship, name2node)
    dag = stream.construct(nodes)

    assert len(dag._name2nodes) == len(contain_nodes)

    for node in dag._name2nodes.values():
        assert node.display_name in contain_nodes


def test__emplate_multiple_times(
    setup_dagstream: tuple[DagStream, dict[str, FunctionalNode]]
):
    stream, _ = setup_dagstream
    n_functions = len(stream._name2node)

    def sample6():
        pass

    _ = stream.emplace(sample6)
    assert len(stream._name2node) == n_functions + 1


# region dagstream with pipe


@pytest.fixture
def setup_dagstream():
    def A():
        return [1, 2]

    def B(*output_by_A: int):
        return {"b": 3}

    def C():
        return {"c": 4}

    def D(output_by_B_and_C):
        pass

    def E():
        pass

    def F():
        pass

    stream = DagStream()
    nodes = stream.emplace(A, B, C, D, E, F)

    name2node = {v.display_name: v for v in nodes}
    return stream, name2node


def test__pipe_dagstream():
    ...


# endregion
