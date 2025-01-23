import multiprocessing as multi
import random
import time
from functools import partial

from dagstream import DagStream
from dagstream.executor import StreamExecutor


def sample1(results: list[int]):
    time.sleep(random.random())
    results.append(1)


def sample2(results: list[int]):
    time.sleep(random.random())
    results.append(2)


def sample3(results: list[int]):
    time.sleep(random.random())
    results.append(3)


def sample4(results: list[int]):
    time.sleep(random.random())
    results.append(4)


def run_dagstream(results: list[int], *, stream: DagStream):
    dag = stream.construct()
    executor = StreamExecutor(dag)
    executor.run(results)


def test__multiprocessing():
    stream = DagStream()
    node1, node2, node3, node4 = stream.emplace(
        sample1, sample2, sample3, sample4
    )

    node1.precede(node2)
    node3.precede(node2)
    node4.succeed(node3)

    n_process = 3
    n_cases = 10
    manager = multi.Manager()
    results = [manager.list() for _ in range(n_cases)]
    start = time.time()

    with multi.Pool(n_process) as pool:
        func = partial(run_dagstream, stream=stream)
        pool.map(func, results)

    end = time.time()

    print(f"elapsed: {end - start}")
    for result in results:
        tmp = list(result)
        tmp.sort()
        assert tmp == [1, 2, 3, 4]


def test__do_not_affect_other_functional_dag_state():
    stream = DagStream()
    node1, node2, node3, node4 = stream.emplace(
        sample1, sample2, sample3, sample4
    )

    node1.precede(node2, node3)
    node3.succeed(node2)
    node4.succeed(node2, node3)

    dag1 = stream.construct()

    nodes = dag1.get_ready()
    dag1.done(*[n.mut_name for n in nodes])

    dag2 = stream.construct()
    nodes = dag2.get_ready()
    assert nodes[0].display_name == "sample1"

    nodes1_2 = dag1.get_ready()
    assert nodes1_2[0].display_name == "sample2"
