import os
import pathlib

import pytest

from dagstream import DagStream
from dagstream.executor import StreamExecutor, StreamParallelExecutor
from dagstream.viewers import MermaidDrawer


def sample1(args: int):
    return args + 10


def sample2(args: int):
    return args + 2


def sample3(*args: int):
    return sum(args)


def sample4(args: int):
    return args


def sample5(args: int):
    return args + 1


def sample6(args: int):
    return args + 3


@pytest.fixture
def construct_stream():
    stream = DagStream()
    node1, node2, node3, node4, node5, node6 = stream.emplace(
        sample1, sample2, sample3, sample4, sample5, sample6
    )

    """
    Relationship

    node1 --> node2 -->   node3
      |                     ^
      ----------------------|
                            |
    node4 --> node5         |
              | --> node6---|
    """
    node1.precede(node2, node3, pipe=True)
    node3.succeed(node1, node2, node6, pipe=True)
    node4.precede(node5, pipe=True)
    node5.precede(node6, pipe=True)

    name2node = {
        node.mut_name: node for node in [node1, node2, node3, node4, node5, node6]
    }
    return stream, name2node


def test__output_figure(construct_stream):
    stream, _ = construct_stream
    viewer = MermaidDrawer()

    dag = stream.construct()

    output_file_path = pathlib.Path(__file__).parent / "sample.mmd"
    viewer.output(dag, file_path=output_file_path)


@pytest.mark.parametrize(
    "mandatory_names, first_args, expected",
    [(["sample4"], (2,), 2), (["sample5"], (5,), 6), (None, (1,), 29)],
)
def test__n_results_when_parallel_executor(
    mandatory_names, first_args, expected, construct_stream
):
    assert os.cpu_count() > 2
    stream, name2node = construct_stream

    if mandatory_names is None:
        mandatory_nodes = None
    else:
        mandatory_nodes = [name2node[name] for name in mandatory_names]

    functional_dag = stream.construct(mandatory_nodes=mandatory_nodes)

    executor = StreamParallelExecutor(functional_dag, n_process=2)

    result = executor.run(first_args=first_args)

    assert len(result) == 1
    for v in result.values():
        assert v == expected


@pytest.mark.parametrize(
    "mandatory_names, first_args, expected",
    [(["sample4"], (2,), 2), (["sample5"], (5,), 6), (None, (1,), 29)],
)
def test__n_results_when_single_executor(
    mandatory_names, first_args, expected, construct_stream
):
    stream, name2node = construct_stream

    if mandatory_names is None:
        mandatory_nodes = None
    else:
        mandatory_nodes = [name2node[name] for name in mandatory_names]

    functional_dag = stream.construct(mandatory_nodes=mandatory_nodes)

    executor = StreamExecutor(functional_dag)

    result = executor.run(first_args=first_args)

    assert len(result) == 1
    for v in result.values():
        assert v == expected
