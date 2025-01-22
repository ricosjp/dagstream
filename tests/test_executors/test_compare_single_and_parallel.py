import os
import time

import pytest

from dagstream import DagStream
from dagstream.executor import StreamExecutor, StreamParallelExecutor


def funcA():
    time.sleep(1)


def funcB():
    time.sleep(1)


def funcC():
    time.sleep(1)


def funcD():
    time.sleep(1)


def funcE():
    time.sleep(1)


@pytest.fixture
def confirm_cpu_count():
    # To perform this test, it is neccesarry 4 cpus
    assert os.cpu_count() >= 4


def test__parallel_run_is_faster_than_single_run(confirm_cpu_count: None):
    stream_parallel = DagStream()
    # All nodes can be run in parallel
    stream_parallel.emplace(funcA, funcB, funcC, funcD)

    start = time.time()
    executor = StreamExecutor(stream_parallel.construct())
    executor.run()
    elapsed_time = time.time() - start

    start = time.time()
    executor = StreamParallelExecutor(stream_parallel.construct(), n_process=4)
    executor.run()
    elapsed_time_parallel = time.time() - start

    print(f"{elapsed_time}, {elapsed_time_parallel}")
    assert elapsed_time > elapsed_time_parallel

    # about 4 times faster than sequetial execution
    assert abs(elapsed_time - elapsed_time_parallel * 4) < 1.0


def test__can_run_in_parallel_with_orders(confirm_cpu_count: None):
    stream = DagStream()
    A, B, C, D, E = stream.emplace(funcA, funcB, funcC, funcD, funcE)

    A.precede(B, C)
    E.succeed(B, C, D)
    D.succeed(C)

    assert os.cpu_count() >= 4
    executor = StreamParallelExecutor(stream.construct(), n_process=4)
    executor.run()
