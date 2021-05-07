===================
Logging and Tagging
===================

-------------------------------------
Direct API calls vs shipping logfiles
-------------------------------------
Sending data to the backend can be achieved by using the Raymon client library. The library offers 2 ways of sending data to the backend. One is through direct API calls by using the :class:`RaymonAPILogger` class, the other one is by logging to text files by using the :class:`RaymonFileLogger` class. Both classes offer the same interface but work differently under the hood. 

In case of the :class:`RaymonFileLogger`, you still have to ship the logfiles to the backend through FluentBit or Filebeat. See Shipping Logs for more info. The advantage of using the `RaymonFileLogger` is that it does not block your code with an API call and detaches your code from the Raymon backend so that your code does not block when the backend is unreachable. For those reasons it is recommended to use the `RaymonFileLogger` class for production use cases. For development and testing, the :class:`RaymonAPILogger` is easier to get started. 

You will probably not use the loggers directly, but instead use a Trace object, as discussed in the section below.

--------------------
Logging using Traces
--------------------
Logging with Raymon is mostly done using the :class:`raymon.Trace` class. This class allows you to instantiate a trace object, which is a wrapper around a :code:`trace_id` and a logger object. This :code:`trace_id` is auto-generated or provided during construction or the object. A :code:`Trace` object can be used as a logger to log info messages or raw data from anywhere in your system. All data connected to the same :code:`trace_id` will belong to the same trace. 

Additionally, you can attach tags to the trace to be able to easily filter traces on the Raymon platform. :class:`raymon.Tag` objects have a name, a value, a type and optionally a group. Tags are what the Raymon backend uses for monitoring, alerting and filtering or traces. Tags can represent anything: metadata, data quality metrics, errors during execution, execution times, etc... Tags are fundamental to how Raymon works. See also Data Profiling.



-------------------
Putting it together
-------------------
The following example demonstrates a small working example of how you can send data to the Raymon backend.

.. code-block:: python
    :linenos:

    class RetinopathyDeployment:
    def __init__(self):
        if USE_FILELOGGER:
            self.raymon = RaymonFileLogger(path=LOG_PATH, project_id=PROJECT_ID)
        else:
            self.raymon = RaymonAPILogger(
                url=RAYMON_URL,
                project_id=PROJECT_ID,
                auth_path=SECRET,
                env=RAYMON_ENV,
            )

    def process(self, trace_id, data, metadata):
        trace = Trace(logger=self.raymon, trace_id=trace_id)
        try:
            trace.info(f"Received prediction request.")
            trace.log(ref="request_data", data=rt.Image(data))
            trace.tag(metadata)

            resized_img = data.resize((512, 512))
            trace.log(ref="resized_data", data=rt.Image(resized_img))
            pred = self.model_predict(data, metadata)
            trace.info(f"Pred: {pred}, {type(pred)}")
            trace.log(ref="model_prediction", data=rt.Native(pred))
            return pred
        except Exception as exc:
            # raise
            print(f"Exception for req_id {trace}: {exc}")
            # raise
            trace.tag(
                Tag(type="error", name=type(exc).__name__, value=str(exc))
            )
            trace.info(traceback.format_exc())
            
            


-----------
Trace class
-----------
.. autoclass:: raymon.Trace
   :members:


---------
Tag class
---------
.. autoclass:: raymon.Tag
   :members:


.. Traces
    Info
    Data & wrappers
    Tags
        - fields: name, value, type, group
        - reserved types
        - tag groups