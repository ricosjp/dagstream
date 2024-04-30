import multiprocessing as multi
import os

import pytest

from dagstream import DagStream
from dagstream.executor import StreamParallelExecutor, _worker
from dagstream.graph_components.nodes import FunctionalNode


def sample1(args: int):
    return args + 1


def sample2(args: int):
    return args + 2


def sample3(*args):
    return 3


def sample4(*args):
    return 4


def sample5(*args):
    return 5


def sample6(*args):
    return 6


@pytest.fixture
def construct_stream():
    stream = DagStream()
    node1, node2, node3, node4, node5, node6 = stream.emplace(
        sample1, sample2, sample3, sample4, sample5, sample6
    )

    """
    Relationship

    node1 --> node2 --> node3
      |                   ^
      --------------------|
      |
      |
      | --> node4 --> node5
              | --> node6
    """
    node1.precede(node2, node3)
    node3.succeed(node2)
    node4.succeed(node1)
    node4.precede(node5, node6)

    name2node = {
        node.display_name: node for node in [node1, node2, node3, node4, node5, node6]
    }
    return stream, name2node


def test__cannot_initialize_before_calling_construct(construct_stream):
    stream, _ = construct_stream

    with pytest.raises(ValueError):
        _ = StreamParallelExecutor(stream)


@pytest.mark.parametrize("n_process", [-1, 0, -100])
def test__not_allowed_non_positive_n_process(n_process, construct_stream):
    stream, _ = construct_stream

    functional_dag = stream.construct()
    with pytest.raises(ValueError):
        _ = StreamParallelExecutor(functional_dag, n_process=n_process)


@pytest.mark.parametrize(
    "mandatory_names, num_of_results, save_state",
    [
        (["sample4"], 1, False),
        (["sample4"], 2, True),
        (["sample5", "sample6"], 2, False),
        (["sample5", "sample6"], 4, True),
    ],
)
def test__n_results_when_parallel_executor(
    mandatory_names, num_of_results, save_state, construct_stream
):
    assert os.cpu_count() > 2
    stream, name2node = construct_stream

    mandatory_nodes = [name2node[name] for name in mandatory_names]
    functional_dag = stream.construct(mandatory_nodes=mandatory_nodes)

    executor = StreamParallelExecutor(functional_dag, n_process=2)

    result = executor.run(0, save_state=save_state)

    assert len(result) == num_of_results


# HACK: NEED to implement by using concurrent.futures
# def test__when_subprocess_is_failed():
#     ...


@pytest.mark.parametrize(
    "inputs, expected",
    [
        ([(sample1, (2,), {})], [3]),
        ([(sample1, (4,), {}), (sample2, (5,), {})], [5, 7]),
    ],
)
def test__worker(inputs, expected):
    input_queue = multi.Queue()
    done_queue = multi.Queue()

    for argvs in inputs:
        func, arg, kwards = argvs
        input_queue.put((FunctionalNode(func), arg, kwards))
    input_queue.put("STOP")

    _worker(input_queue, done_queue)

    assert done_queue.qsize() == len(inputs)

    idx = 0
    while not done_queue.empty():
        func, result = done_queue.get()
        assert result == expected[idx]
        idx += 1
