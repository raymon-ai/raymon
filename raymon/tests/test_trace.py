#%%
import raymon
from raymon.trace import Trace

import pytest


class MockLogger:
    # def __init__(self, context="testing", project_id="default"):
    # super().__init__(context=context, project_id=project_id)
    """
    Functions related to logging of rays
    """

    def log(self, trace_id, ref, data):
        pass

    def flush(self):
        pass


def test_set_global_noneset():
    raymon.clear_trace()
    with pytest.raises(raymon.TraceException):
        trace = raymon.current_trace()


def test_set_global():
    raymon.clear_trace()
    logger = MockLogger()
    trace = Trace(logger=logger)
    trace2 = raymon.current_trace()
    assert trace == trace2


def test_not_set_global():
    raymon.clear_trace()
    logger = MockLogger()
    trace = Trace(logger=logger, set_global=False)
    with pytest.raises(raymon.TraceException):
        raymon.current_trace()


def test_not_set_global_one():
    raymon.clear_trace()
    logger = MockLogger()
    trace1 = Trace(logger=logger, set_global=False)
    trace2 = Trace(logger=logger)
    trace3 = raymon.current_trace()
    assert trace1 != trace2
    assert trace2 == trace3
