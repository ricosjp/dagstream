class DagStreamCycleError(ValueError):
    """Subclass of ValueError raises if a cycle is found in graph."""

    pass


class DagStreamNotReadyError(ValueError):
    """Subclass of ValueError raises by INodeState if some attributes are accessed
    unless nodes state is properly prepared.
    """

    pass
