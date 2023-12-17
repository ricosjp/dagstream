import time

from dagstream import DagStream
from dagstream.executor import StreamExecutor, StreamParallelExecutor

# region Test for Parallel Execution


def funcA():
    time.sleep(1)


def funcB():
    time.sleep(1)


def funcC():
    time.sleep(1)


def funcD():
    time.sleep(1)


def test__parallel_run_is_faster_than_single_run():
    stream_parallel = DagStream()
    # All nodes can be run in parallel
    stream_parallel.emplace(funcA, funcB, funcC, funcD)

    start = time.time()
    executor = StreamExecutor(stream_parallel.construct())
    executor.run()
    elapsed_time = time.time() - start

    start = time.time()
    executor = StreamParallelExecutor(stream_parallel.construct(), n_processes=4)
    executor.run()
    elapsed_time_parallel = time.time() - start

    print(f"{elapsed_time}, {elapsed_time_parallel}")
    assert elapsed_time > elapsed_time_parallel

    # about 4 times faster than sequetial execution
    assert abs(elapsed_time - elapsed_time_parallel * 4) < 1.0


# endregion
