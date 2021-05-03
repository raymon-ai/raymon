import uuid
import numpy as np


def _parse_trace_id(trace_id):
    # rayid is a tuple, with an element per level
    if isinstance(trace_id, str):
        return (trace_id,)
    elif isinstance(trace_id, tuple):
        return trace_id
    elif trace_id is None:
        return (str(uuid.uuid4()),)


def _match_prefix(raylist):
    ids = [str(ray) for ray in raylist]
    shortest_idx = np.argmin(len(idstr) for idstr in ids)
    shortest = ids[shortest_idx]

    for i in range(len(shortest) - 1):
        if not all(idstr.startswith(shortest[: i + 1]) for idstr in ids):
            if i == 1:
                raise Exception(f"No common prefix found for rays: {raylist}")
            break
    match_len = i
    prefix = tuple(shortest[:match_len].split(":"))
    return prefix


class Trace:
    def __init__(self, logger, trace_id=None, pred=None):
        self.trace_id = _parse_trace_id(trace_id)
        self.logger = logger
        self.pred = pred

    """
    Methods related to data logging
    """

    def info(self, text):
        self.logger.info(trace_id=str(self), text=text)

    def log(self, ref, data):
        self.logger.log(trace_id=str(self), ref=ref, data=data)

    def tag(self, tags):
        self.logger.tag(trace_id=str(self), tags=tags)

    def log_input(self, profile, data):
        ref = f"#{profile.name}@{profile.version}-input"
        self.logger.log(trace_id=str(self), ref=ref, data=data)

    def log_output(self, profile, data):
        ref = f"#{profile.name}@{profile.version}-output"
        self.logger.log(trace_id=str(self), ref=ref, data=data)

    def log_actual(self, profile, data):
        ref = f"#{profile.name}@{profile.version}-actual"
        self.logger.log(trace_id=str(self), ref=ref, data=data)

    """
    Methods related to splitting and merging
    """

    def split(self, suffix=None):
        if suffix is None:
            suffix = uuid.uuid4()
        new_id = self.trace_id + (suffix,)
        return Trace(self.logger, trace_id=new_id, pred=self)

    @classmethod
    def merge(cls, raylist, suffix):
        # Check whether it is a list
        if not isinstance(raylist, list):
            raise ValueError("Input type should be a list of Rays")
        # Find prefix that matches all rays
        prefix = _match_prefix(raylist)
        ref_logger = raylist[0].logger
        # Add suffix
        new_id = prefix + (suffix,)
        return Trace(ref_logger, trace_id=new_id, pred=raylist)

    def __str__(self):
        return ":".join(self.trace_id)
