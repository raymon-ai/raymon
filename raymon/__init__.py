from raymon.api import RaymonAPI
from raymon.loggers import RaymonFileLogger, RaymonAPILogger
from raymon.trace import Trace
from raymon.tags import Tag
from raymon.globals import Serializable, DataException
from raymon.profiling.profiles import ModelProfile
from raymon.profiling.components import (
    InputComponent,
    OutputComponent,
    ActualComponent,
    EvalComponent,
    DataType,
    Component,
)
from raymon.profiling.stats import IntStats, FloatStats, CategoricStats, Stats
from raymon.profiling.extractors import Extractor

from .version import __version__

__current_trace = None


class TraceException(Exception):
    pass


def set_current_trace(trace):
    global __current_trace
    if not isinstance(trace, Trace):
        raise TypeError(f"trace is not of type Trace")
    __current_trace = trace


def current_trace():
    if isinstance(__current_trace, Trace):
        return __current_trace
    else:
        raise TraceException("No current Trace set")


def clear_trace():
    global __current_trace
    __current_trace = None
