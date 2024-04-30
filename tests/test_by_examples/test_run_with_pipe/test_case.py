import os
import pathlib

import pytest

from dagstream import DagStream
from dagstream.executor import StreamExecutor, StreamParallelExecutor
from dagstream.viewers import MermaidDrawer


def A(vals: list[int], offset: int):
    return [v + offset for v in vals]


def B(output_by_A: list[int]):
    return sum(output_by_A)


def C(output_by_B: int):
    return output_by_B + 10


def D(*output_by_B_and_C: list[int]):
    return sum(output_by_B_and_C)


@pytest.fixture
def construct_stream():
    stream = DagStream()
    funcA, funcB, funcC, funcD = stream.emplace(A, B, C, D)

    funcA.precede(funcB, pipe=True)
    funcC.succeed(funcB, pipe=True)
    funcD.succeed(funcB, funcC, pipe=True)

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

    result = executor.run(first_args=([1, 2], 3))
    actual = result["D"]

    assert actual == 28


def test__single_pipe_dagstream(construct_stream):
    stream = construct_stream

    func_dag = stream.construct()
    executor = StreamExecutor(func_dag)

    result = executor.run(first_args=([1, 2], 3))

    actual = result["D"]

    assert actual == 28
