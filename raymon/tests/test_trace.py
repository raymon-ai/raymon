#%%
from raymon.trace import Trace


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


def test_split():
    logger = MockLogger()
    base_ray = Trace(logger=logger, trace_id="base")
    child = base_ray.split(suffix="a")
    assert child.trace_id == ("base", "a")


def test_split_tuple():
    logger = MockLogger()
    base_ray = Trace(logger=logger, trace_id=("base", "split"))
    child = base_ray.split(suffix="a")
    assert child.trace_id == ("base", "split", "a")


def test_merge():
    logger = MockLogger()
    base_ray = Trace(logger=logger, trace_id="base")
    children = [base_ray.split(suffix=str(i)) for i in range(10)]

    for child in children:
        assert len(child.trace_id) == 2
    merged_a = Trace.merge(raylist=children[:5], suffix="head")
    merged_b = Trace.merge(raylist=children[:5], suffix="tail")

    for i, pred in enumerate(merged_a.pred):
        pred == children[i]

    for i, pred in enumerate(merged_b.pred):
        pred == children[5 + i]
