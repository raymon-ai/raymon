# Trace class

 _class_ `raymon.Trace`\(_logger_, _trace\_id=None_, _set\_global=True_\)[¶](trace-class.md#raymon.Trace)

The Trace class can be used to trace data trough your system. You can use a Trace object to log text just like any other logger, but you can also use it to log data and tag the traces with metadata.Parameters

* **logger** \(`RaymonLoggerBase`\) – The logger to use. Can be either [`RaymonFileLogger`](loggers.md#raymon.RaymonFileLogger) for logging to a text file, or [`RaymonAPILogger`](loggers.md#raymon.RaymonAPILogger) for user direct API calls to the backend.
* **trace\_id** \(_str_\) – The id for the trace. If None, a uuid will be auto-generated.

 `__init__`\(_logger_, _trace\_id=None_, _set\_global=True_\)[¶](trace-class.md#raymon.Trace.__init__)

Initialize self. See help\(type\(self\)\) for accurate signature. `info`\(_text_\)[¶](trace-class.md#raymon.Trace.info)

Log a text message.Parameters

**text** \(_str_\) – The string you want to log to the backend. `log`\(_ref_, _data_\)[¶](trace-class.md#raymon.Trace.log)

Log a data artefact to the backend.Parameters

* **ref** \(_str_\) – A reference name to refer to this artefact later. This reference name, in combination with the trace id should be unique.
* **data** \([`raymon.types.RaymonDataType`](data-types.md#raymon.types.RaymonDataType) or `raymon.globals.Serializable`\) – The data you want to log to the backend.

 `tag`\(_tags_\)[¶](trace-class.md#raymon.Trace.tag)

Tag the trace with given tags.Parameters

**tags** \(list of dicts or list of [`raymon.Tag`](tag-class.md#raymon.Tag)\) – A

