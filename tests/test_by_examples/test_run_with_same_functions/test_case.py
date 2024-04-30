import os
import pathlib

import pytest

from dagstream import DagStream
from dagstream.executor import StreamExecutor, StreamParallelExecutor
from dagstream.viewers import MermaidDrawer


def increment(val: int, *, inc: int = 1):
    return val + inc


def summation(*val: int, **kwards):
    return sum(val)


@pytest.fixture
def construct_stream():
    stream = DagStream()
    funcA0, funcA1, funcA2, funcB = stream.emplace(
        increment, increment, increment, summation
    )

    funcA0.precede(funcA1, pipe=True)
    funcA1.precede(funcA2, funcB, pipe=True)
    funcA2.precede(funcB, pipe=True)

    return stream


def test__output_figure(construct_stream):
    stream: DagStream = construct_stream
    viewer = MermaidDrawer()

    dag = stream.construct()

    output_file_path = pathlib.Path(__file__).parent / "sample.mmd"
    viewer.output(dag, file_path=output_file_path)


def test__parallel_executor_with_pipe(construct_stream):
    assert os.cpu_count() > 2
    stream = construct_stream
    functional_dag = stream.construct()

    executor = StreamParallelExecutor(functional_dag, n_process=2)

    result = executor.run(first_args=(3,), inc=2)
    actual = result["summation"]

    assert actual == 16


def test__single_pipe_dagstream(construct_stream):
    stream = construct_stream

    func_dag = stream.construct()
    executor = StreamExecutor(func_dag)

    result = executor.run(first_args=(3,), inc=2)
    actual = result["summation"]

    assert actual == 16
