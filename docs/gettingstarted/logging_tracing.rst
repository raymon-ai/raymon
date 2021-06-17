===============
Traces and Tags
===============

The Raymon client library allows you to log text, data and tags to the backend. This can be done using the API's :meth:`raymon.RaymonAPI.post` method, but is simplified by using the :class:`raymon.Trace` class.

A :class:`raymon.Trace` object is a small object with a unique `id` per request. It can be used to send data to the Raymon backend and connects all data logged with the same `id` to the same request, forming a *trace* of how the data was processed. You can log data from anywhere in your code, even over different services. As long as it is connected to the same `id`, Raymon will connect it to the relevant trace. Creating a :class:`raymon.Trace` object also requires an intantiated logger, as discussed in :ref:`Loggers: direct API calls vs shipping logfiles` below.

----------------------------------------------
Loggers: direct API calls vs shipping logfiles
----------------------------------------------
Upon initialization, the :class:`raymon.Trace` object requires a `logger` parameter of type :class:`raymon.loggers.RaymonLoggerBase`. This logger is used by the Trace object and takes care of sending data to the backend. The library offers 2 options of sending data to the backend. One is through direct API calls by using the :class:`raymon.RaymonAPILogger` class, the other one is by logging to text files by using the :class:`raymon.RaymonFileLogger` class. Both classes offer the same interface but work differently under the hood. 

The :class:`raymon.RaymonAPILogger` uses direct REST API calls to send data syncronously to the backend. This is great for testing and development, but blocks your code until the data is successfully sent and will crash when the backend can be reached. You should probably not use it in production settings.

The :class:`raymon.RaymonFileLogger` simply serializes all data to a text file that must then be shipped to the backend through FluentBit or Filebeat. The advantage of using the :class:`raymon.RaymonFileLogger` is that it does not block your code with an API call and detaches your code from the Raymon backend. For those reasons it is recommended to use the :class:`raymon.RaymonFileLogger` class for production use cases. 

--------
Examples
--------

Enough talk, lets see some examples, right? This section lists some of the code from on of the examples: `examples/0-setup-logging.ipynb`.

In the code snippet below, we create an :class:`raymon.RaymonAPILogger` logger first, and then pass it as a parameter when constructing a :class:`raymon.Trace` object. We do not pass a `trace_id`, which means a `uuid` will be auto generated. If you alreay have a `uuid`, you can pass it as `trace_id`.

After construction, we can use the trace object like a logger to log text mesages.

.. code-block:: python
    :linenos:

    from raymon import Trace, RaymonAPILogger

    logger = RaymonAPILogger(project_id=project_id)
    trace = Trace(logger=logger, trace_id=None) 
    

Logging Text
------------
You can use the trace like any other logger to log info text messages, as shown below.

.. code-block:: python
    :linenos:

    trace.info("You can log whatever you want here")


Logging Tags
------------

Additionally, you can attach tags to the trace. :class:`raymon.Tag` objects have a :code:`name`, a :code:`value`, a :code:`type` and optionally a :code:`group`. Tags are what the Raymon backend uses for monitoring and alerting. Tags can represent anything: metadata, data quality metrics, errors during execution, execution times, etc... Tags are fundamental to how the Raymon backend works: tags allow you to filter and query data, tag cominations define slices and tags are used for monitoring and alerting.

.. code-block:: python
    :linenos:
    
    from raymon import Tag

    tags = [
        # Using a dict
        {
            "name": "client",
            "value": "bigshot_client",
            "type": "label"
        },
        # Using the Tag ogbject
        Tag(name="sdk_version", value="1.4.2", type="label"),
        Tag(name="prediction_time_ms", value="120", type="metric")
    ]
    trace.tag(tags)



Logging Data
------------
Raymon allows you to log data artefacts to the backend too. The artefacts have a reference that must be unique within the trace and which allows you to fetch them from the backend whenever you want. By default, these artefacts are simply stored, although you can do extra processing on them with some configuration in the project manifest. (Explained in other tutorials.)

All data that is logged to the Raymn platform is serialized to JSON, so all data must be serializable. Raymon offers data wrappers for popular data types that will take care of serializing your data in the `raymon.types` module. Of course, you can also define your own wrappers if you need them by implementing the :class:`raymon.types.RaymonDataType` interface.

.. code-block:: python
    :linenos:
    
    import pandas as pd
    import numpy as np
    from PIL import Image

    import raymon.types as rt


    img = Image.open("./data_sample/castinginspection/def_front/cast_def_0_0.jpeg")
    arr = np.array([[1, 2], [3, 4]])
    df = pd.DataFrame(arr, columns=['a', 'b'])

    trace.log(ref="native-reff", data=rt.Native(
        {"foo": "bar", 
        "whatever": ["you", "want"], 
        "all_native_types": 1}))
    trace.log(ref="numpy-ref", data=rt.Numpy(arr))
    trace.log(ref="pandas-ref", data=rt.DataFrame(df))
    trace.log(ref="image-ref", data=rt.Image(img))




-------------------------------
Retrieving Traces and Artefacts
-------------------------------
After logging this data, you can navigate to the `web UI <https://ui.raymon.ai>`_ and navigate to the Traces tab. There, you shoudl see one trace, with 3 tags. When clicking on the eye icon, the trace should open and you should see the tags, text and data you have logged as shown below.

.. figure:: screens/logged_data.png
  :width: 800
  :alt: The Traces view after logging some data.
  :class: with-shadow with-border

You can fetch data from the backend for further debugging or analysis by clicking the download icon next to each data artefact, or download the complete trace by clicking the icon next to the Logs header.

For example, the code to fetch an artefact could look as follows:

.. code-block:: python

    resp = api.object_search(project_id="d6ac1bf0-4e22-43ae-a85e-3cb2c1e5da80", trace_id="472b649d-cce8-4d50-9682-6b81a80755c0", ref="numpy-ref")

    if not resp.ok:
        raise Exception("Something wrong.")

    data = resp.json()
    obj_id = data["obj_id"]
    obj_data = data["obj_data"]

    raymon_wrapped = rt.load_jcr(obj_data)
    orig = raymon_wrapped.data