from __future__ import annotations

import multiprocessing as multi
from typing import Any

from dagstream.graph_components import FunctionalDag


class StreamExecutor:
    def __init__(self, functional_dag: FunctionalDag) -> None:
        """Executor for FunctionalDag Object.

        Parameters
        ----------
        functional_dag : FunctionalDag
            FunctionalDag instance which is already
             constructed from DagStream Object

        Raises
        ------
        ValueError
            _description_
        """
        if not isinstance(functional_dag, FunctionalDag):
            raise ValueError(
                "functional_dag is not a instance of FunctionalDag. "
                "Maybe, you forget to call 'your_dagstream.construct()'"
                "  beforehand."
            )
        self._dag = functional_dag

    def run(
        self,
        *args: Any,  # noqa: ANN401
        first_args: tuple[Any] | None = None,
        save_all_state: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        """Run functions sequencially according to static order.

        Input parameters are passed to all functions.

        Returns
        -------
        dict[str, Any]
            Key is name of function, value is returned objects
              from each function.
        """
        results: dict[str, Any] = {}

        while self._dag.is_active:
            nodes = self._dag.get_ready()
            for node in nodes:
                if node.n_predecessors == 0 and first_args is not None:
                    for arg in first_args:
                        node.receive_args(arg)

                result = node.run(*args, **kwargs)
                self._dag.send(node.mut_name, result)
                self._dag.done(node.mut_name)

                if self._dag.check_last(node) or save_all_state:
                    results.update({node.mut_name: result})

        return results


class StreamParallelExecutor:
    """Parallel Executor for FunctionalDag Object."""

    def __init__(
        self, functional_dag: FunctionalDag, n_process: int = 1
    ) -> None:
        """THIS IS EXPERIMENTAL FEATURE. Parallel Executor
          for FunctionalDag Object.

        Parameters
        ----------
        functional_dag : FunctionalDag
            FunctionalDag instance which is already constructed
              from DagStream Object
        n_processes : int, optional
            The number of processes to run in parallel, by default 1

        Raises
        ------
        ValueError
            raise this error when n_processes is lower than 0
        """
        if not isinstance(functional_dag, FunctionalDag):
            raise ValueError(
                "functional_dag is not a instance of FunctionalDag. "
                "Maybe, you forget to call 'your_dagstream.construct()'"
                " beforehand."
            )

        self._dag = functional_dag
        self._n_processes = n_process
        if self._n_processes <= 0:
            raise ValueError(
                f"n_processes must be larger than 0. Input: {n_process}"
            )

    def run(
        self,
        *args: Any,  # noqa: ANN401
        first_args: tuple[Any] | None = None,
        save_all_state: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        """Run functions in parallel.

        Parameters are passed to all functions.
        Please note that parameters are not shared between multiple processes.

        Returns
        -------
        dict[str, Any]
            Key is name of function, value is returned objects
              from each function.
        """
        task_queue: multi.Queue = multi.Queue()
        done_queue: multi.Queue = multi.Queue()
        all_processes: list[multi.Process] = []

        results: dict[str, Any] = {}

        while self._dag.is_active:
            nodes = self._dag.get_ready()

            for node in nodes:
                if node.n_predecessors == 0 and first_args is not None:
                    for arg in first_args:
                        node.receive_args(arg)

                task_queue.put((node, args, kwargs))

            # Start worker processes
            n_left_process = self._n_processes - len(all_processes)
            for _ in range(n_left_process):
                process = multi.Process(
                    target=_worker, args=(task_queue, done_queue)
                )
                process.start()
                all_processes.append(process)

            while not done_queue.empty():
                _done_node, _result = done_queue.get()

                # NOTE: When using multiprocessing, id(IFunctionalNode)
                # after running is not the same as one before running.

                self._dag.send(_done_node.mut_name, _result)
                self._dag.done(_done_node.mut_name)

                if self._dag.check_last(_done_node) or save_all_state:
                    results.update({_done_node.mut_name: _result})

            if not self._dag.is_active:
                for _ in range(self._n_processes):
                    task_queue.put("STOP")

        return results


def _worker(input_queue: multi.Queue, done_queue: multi.Queue):
    for func, args, kwargs in iter(input_queue.get, "STOP"):
        result = func.run(*args, **kwargs)
        done_queue.put((func, result))
