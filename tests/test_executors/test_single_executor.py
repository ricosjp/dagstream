import pytest

from dagstream import DagStream
from dagstream.executor import StreamExecutor


def sample1(*args, **kwards):
    return args, kwards


def sample2(*args, **kwards):
    return args, kwards


def sample3(*args, **kwards):
    return args, kwards


def sample4(*args, **kwards):
    return args, kwards


def sample5(*args, **kwards):
    return args, kwards


def sample6(*args, **kwards):
    return args, kwards


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
    node1.precede(node2, node3)
    node3.succeed(node1, node2, node6)
    node4.precede(node5)
    node5.precede(node6)

    name2node = {
        node.display_name: node for node in [node1, node2, node3, node4, node5, node6]
    }
    return stream, name2node


def test__cannot_initialize_before_calling_construct(construct_stream):
    stream, _ = construct_stream

    with pytest.raises(ValueError):
        _ = StreamExecutor(stream)


@pytest.mark.parametrize(
    "mandatory_names, num_of_results, save_all_state",
    [
        (["sample5"], 1, False),
        (["sample5"], 2, True),
        (["sample3", "sample6"], 1, False),
        (["sample3", "sample6"], 6, True),
        (["sample1", "sample5"], 3, True),
    ],
)
def test__n_results_when_parallel_executor(
    mandatory_names, num_of_results, save_all_state, construct_stream
):
    stream, name2node = construct_stream

    mandatory_nodes = [name2node[name] for name in mandatory_names]
    functional_dag = stream.construct(mandatory_nodes=mandatory_nodes)

    executor = StreamExecutor(functional_dag)

    result = executor.run(save_all_state=save_all_state)

    assert len(result) == num_of_results


@pytest.mark.parametrize(
    "mandatory_names, first_args, first_names",
    [
        (["sample4"], (1,), ["sample4"]),
        (["sample3"], (10,), ["sample4", "sample1"]),
        (None, (12, 22, 30), ["sample4", "sample1"]),
        (["sample2"], (1, 5), ["sample1"]),
    ],
)
def test__pass_first_args(mandatory_names, first_args, first_names, construct_stream):
    stream, name2node = construct_stream

    if mandatory_names is None:
        mandatory_nodes = None
    else:
        mandatory_nodes = [name2node[name] for name in mandatory_names]
    functional_dag = stream.construct(mandatory_nodes=mandatory_nodes)

    executor = StreamExecutor(functional_dag)
    result = executor.run(save_all_state=True, first_args=first_args)

    for name in first_names:
        assert result[name][0] == first_args


@pytest.mark.parametrize(
    "mandatory_names, args, kwards",
    [(["sample4"], (1,), {"a": 3}), (None, (11, 12, 13), {"sample": 12})],
)
def test__pass_common_args(mandatory_names, args, kwards, construct_stream):
    stream, name2node = construct_stream

    if mandatory_names is None:
        mandatory_nodes = None
    else:
        mandatory_nodes = [name2node[name] for name in mandatory_names]
    functional_dag = stream.construct(mandatory_nodes=mandatory_nodes)

    executor = StreamExecutor(functional_dag)
    result = executor.run(*args, **kwards, save_all_state=True)

    assert len(result) > 0
    for v in result.values():
        assert v[0] == args
        assert v[1] == kwards
