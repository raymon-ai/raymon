import uuid
import numpy as np

import raymon
from raymon.loggers import BatchedAPILogger


def _parse_trace_id(trace_id):
    if isinstance(trace_id, str):
        return trace_id
    else:
        return str(uuid.uuid4())


class Trace:

    """The Trace class can be used to trace data trough your system. You can use a Trace object to log text just like any other logger, but you can also use it to log data and tag the traces with metadata.

    Parameters
    ----------

    logger : :class:`RaymonLoggerBase`
        The logger to use. Can be either :class:`RaymonFileLogger` for logging to a text file, or :class:`RaymonAPILogger` for user direct API calls to the backend.
    trace_id : str
        The id for the trace. If None, a uuid will be auto-generated.

    """

    def __init__(self, logger, trace_id=None, set_global=True):

        self.trace_id = _parse_trace_id(trace_id)
        self.logger = logger
        self.set_global = set_global
        if set_global:
            raymon.set_current_trace(self)

    """
    Methods related to data logging
    """

    def info(self, text, flush=False):
        """
        Log a text message.

        Parameters
        ----------
        text : str
            The string you want to log to the backend.
        """
        if isinstance(self.logger, BatchedAPILogger):
            self.logger.info(trace_id=self.trace_id, text=text, flush=flush)
        else:
            self.logger.info(trace_id=self.trace_id, text=text)

    def log(self, ref, data, flush=False):
        """Log a data artefact to the backend.

        Parameters
        ----------
        ref : str
            A reference name to refer to this artefact later. This reference name, in combination with the trace id should be unique.
        data : :class:`raymon.types.RaymonDataType` or :class:`raymon.globals.Serializable`
            The data you want to log to the backend.
        """
        if isinstance(self.logger, BatchedAPILogger):
            self.logger.log(trace_id=self.trace_id, ref=ref, data=data, flush=flush)
        else:
            self.logger.log(trace_id=self.trace_id, ref=ref, data=data)

    def tag(self, tags, flush=False):
        """Tag the trace with given tags.

        Parameters
        ----------
        tags : list of dicts or list of :class:`raymon.Tag`
             A
        """
        if isinstance(self.logger, BatchedAPILogger):
            self.logger.tag(trace_id=self.trace_id, tags=tags, flush=flush)
        else:
            self.logger.tag(trace_id=self.trace_id, tags=tags)

    def __str__(self):
        return self.trace_id
