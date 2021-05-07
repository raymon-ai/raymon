import uuid
import numpy as np


def _parse_trace_id(trace_id):
    if isinstance(trace_id, str):
        return (trace_id,)
    # elif isinstance(trace_id, tuple):
    #     return trace_id
    else:
        return (str(uuid.uuid4()),)


class Trace:

    """The Trace class can be used to trace data trough your system. You can use a Trace object to log text just like any other logger, but you can also use it to log data and tag the traces with metadata.

    Parameters
    ----------

    logger : :class:`RaymonLoggerBase`
        The logger to use. Can be either :class:`RaymonFileLogger` for logging to a text file, or :class:`RaymonAPILogger` for user direct API calls to the backend.
    trace_id : str
        The id for the trace. If None, a uuid will be auto-generated.

    """

    def __init__(self, logger, trace_id=None):

        self.trace_id = _parse_trace_id(trace_id)
        self.logger = logger

    """
    Methods related to data logging
    """

    def info(self, text):
        """
        Log a text message.

        Parameters
        ----------
        text : str
            The string you want to log to the backend.
        """
        self.logger.info(trace_id=str(self), text=text)

    def log(self, ref, data):
        """Log a data artefact to the backend.

        Parameters
        ----------
        ref : str
            A reference name to refer to this artefact later. This reference name, in combination with the trace id should be unique.
        data : raymon.types.RaymonDataType
            The data you want to log to the backend.
        """
        self.logger.log(trace_id=str(self), ref=ref, data=data)

    def tag(self, tags):
        """Tag the trace with given tags.

        Parameters
        ----------
        tags : list of dicts or list of :class:`raymon.Tag`
             A
        """
        self.logger.tag(trace_id=str(self), tags=tags)

    def log_profile_input(self, profile, data):
        ref = f"#{profile.name}@{profile.version}-input"
        self.logger.log(trace_id=str(self), ref=ref, data=data)

    def log_profile_output(self, profile, data):
        ref = f"#{profile.name}@{profile.version}-output"
        self.logger.log(trace_id=str(self), ref=ref, data=data)

    def log_profile_actual(self, profile, data):
        ref = f"#{profile.name}@{profile.version}-actual"
        self.logger.log(trace_id=str(self), ref=ref, data=data)
