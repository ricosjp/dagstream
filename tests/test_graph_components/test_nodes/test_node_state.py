import pytest

from dagstream.utils.errors import DagStreamNotReadyError
from dagstream.graph_components.nodes.node_state import ReadyNodeState, UnReadyNodeState



def test__unready_state():
    state = UnReadyNodeState()
    with pytest.raises(DagStreamNotReadyError):
        state.forward()


@pytest.mark.parametrize("n_predecessors", [
    10, 2, 3
])
def test__ready_state_initialized(n_predecessors: int):
    state = ReadyNodeState(n_predecessors)

    assert state.n_predecessors == n_predecessors
    assert not state.is_ready


@pytest.mark.parametrize("n_predecessors", [
    10, 2, 3
])
def test__check_is_finished(n_predecessors: int):
    state = ReadyNodeState(n_predecessors)

    for _ in range(n_predecessors):
        assert not state.is_ready
        state.forward()

    assert state.is_ready

    state.forward()
    assert state.is_finished
