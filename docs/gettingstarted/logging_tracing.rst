===============
Traces and Tags
===============

To be able to use the Raymon platform, you have to feed it some data. The code snippet below illustrates how this can be done for a ficticious deployment that checks images of retinas for Retinopathy.

.. code-block:: python
    :linenos:

    class RetinopathyDeployment:
        def __init__(self):
            if USE_FILELOGGER:
                self.raymon = RaymonFileLogger(path="/var/log/raymon", 
                                               project_id="your project id")
            else:
                self.raymon = RaymonAPILogger(
                    url="https://api.your-raymon.ai/v0",
                    project_id="your project id",

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
                trace.tag(
                    [Tag(type="error", name=type(exc).__name__, value=str(exc))]
                )
                trace.info(traceback.format_exc())



-------------------------------------
Direct API calls vs shipping logfiles
-------------------------------------
Sending data to the backend can be achieved by using the Raymon client library. The library offers 2 ways of sending data to the backend. One is through direct API calls by using the :class:`RaymonAPILogger` class, the other one is by logging to text files by using the :class:`RaymonFileLogger` class. Both classes offer the same interface but work differently under the hood. 

In case of the :class:`RaymonFileLogger`, you still have to ship the logfiles to the backend through FluentBit or Filebeat. See Shipping Logs for more info. The advantage of using the :class:`RaymonFileLogger` is that it does not block your code with an API call and detaches your code from the Raymon backend. For those reasons it is recommended to use the :class:`RaymonFileLogger` class for production use cases. For development and testing, the :class:`RaymonAPILogger` is easier to get started. 

You will probably not use the loggers directly, but instead use a Trace object, as discussed in the section below.

---------------------------
Traces: Logging and Tagging
---------------------------
Logging with Raymon is mostly done using the :class:`raymon.Trace` class. This class allows you to instantiate a trace object, which is a wrapper around a :code:`trace_id` and a logger object, as described in :ref:`Direct API calls vs shipping logfiles`. This :code:`trace_id` is auto-generated or provided during construction or the object. A :code:`Trace` object can be used as a logger to log info messages or raw data from anywhere in your system. In the code snippet above, the :code:`trace` is instantiated in the entry method on line 13.

Logging Text
------------
Just like as with any other logger, you can use the :code:`trace` to log text messages, as on line 15.

Logging Data
------------
When logging data, a :code:`ref` is required that must a unique over all log statements in the trace so that the combination of :code:`trace_id` and :code:`ref` is globally unique. The  :code:`trace_id` and :code:`ref` allow you to identify the logged artefact and query it using the API later. This is illustrated on line 16. 

All data that is logged to the Raymn platform is serialized to JSON, thus all data must be serializable. We offer common data types out of the box in the :py:mod:`raymon.types` module. You can easliy define your own data typesby implementing the :class:`raymon.types.RaymonDataType` interface.

Tagging
-------
Additionally, you can attach tags to the trace to be able to easily filter traces on the Raymon platform. :class:`raymon.Tag` objects have a :code:`name`, a :code:`value`, a :code:`type` and optionally a :code:`group`. Tags are what the Raymon backend uses for monitoring and alerting. Tags can represent anything: metadata, data quality metrics, errors during execution, execution times, etc... Tags are fundamental to how Raymon works. See also Data Profiling.


-------------------------------
Retrieving Traces and Artefacts
-------------------------------
TODO: Basic usage, Link to extended example related to filtering and slicing?