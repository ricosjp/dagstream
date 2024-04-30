import pytest

from dagstream.graph_components.nodes.node_state import ReadyNodeState, UnReadyNodeState
from dagstream.utils.errors import DagStreamNotReadyError


def test__unready_state_forward():
    state = UnReadyNodeState()
    with pytest.raises(DagStreamNotReadyError):
        state.forward()


def test__unready_state_n_predecessors():
    state = UnReadyNodeState()
    with pytest.raises(DagStreamNotReadyError):
        _ = state.n_predecessors


def test__unready_state_is_finished():
    state = UnReadyNodeState()
    with pytest.raises(DagStreamNotReadyError):
        _ = state.is_finished


def test__unready_state_is_ready():
    state = UnReadyNodeState()
    assert not state.is_ready


@pytest.mark.parametrize("n_predecessors", [10, 2, 3])
def test__ready_state_initialized(n_predecessors: int):
    state = ReadyNodeState(n_predecessors)

    assert state.n_predecessors == n_predecessors
    assert not state.is_ready


@pytest.mark.parametrize("n_predecessors", [10, 2, 3])
def test__check_is_finished(n_predecessors: int):
    state = ReadyNodeState(n_predecessors)

    for _ in range(n_predecessors):
        assert not state.is_ready
        state.forward()

    assert state.is_ready

    state.forward()
    assert state.is_finished
