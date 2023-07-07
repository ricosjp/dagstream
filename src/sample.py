import dagstream
from dagstream.viewers.viewer import MermaidDrawer
from dagstream.executor import StreamExecutor


def funcA():
    print("funcA")
    return None


def funcB():
    print("funcB")
    return None


def funcC():
    print("funcC")
    return None


def funcD():
    print("funcD")
    return None


def funcE():
    print("funcE")
    return None


def funcF():
    print("funcF")
    return None


stream = dagstream.DagStream()
A, B, C, D, E, F = stream.emplace(funcA, funcB, funcC, funcD, funcE, funcF)

A.precede(B, C)
E.succeed(B, C, D)
D.succeed(C)
F.succeed(E)

executor = StreamExecutor()

viewer = MermaidDrawer()
import pathlib

graph = stream.construct(mandatory_nodes={D})

executor.run(graph)
viewer.output(graph, file_path=pathlib.Path("outputs/sample.md"))
