---
description: >-
  How to make you model predictions traceable and debuggable using the Raymon
  platform.
---

# Tracing predictions

Using Raymon, you can log data, messages and tags to the backend. Of course you need to have the backend set up for this. Since we're still in private alpha, please [contact us](https://raymon.ai) if you want to do so. This can be done by using our cloud hosted API, bit you can also host it yourself.

## Creating a Trace

In the code snippet below, we create an `raymon.RaymonAPILogger` logger first, and then pass it as a parameter when constructing a `raymon.Trace` object. We do not pass a `trace_id`, which means a `uuid` will be auto generated for this trace. If you already have a `uuid`, you can pass it as `trace_id`.

```python
from raymon import Trace, RaymonAPILogger

logger = RaymonAPILogger(project_id=project_id)
trace = Trace(logger=logger, trace_id=None)
```

After construction, we can use the trace object like a logger to log text, data and metadata.

### Logging Text

You can use the trace like any other logger to log info text messages, as shown below.

```python
trace.info("You can log whatever you want here")
```

### Logging Tags

Additionally, you can attach tags to the trace. Tags are fundamental to how the Raymon backend works and are what the Raymon backend uses for monitoring and alerting. Tags can represent anything: metadata, data quality metrics, errors during execution, execution times, etc… Furthermore, tags allow you to filter and query data, and tag combinations define slices. We have already encountered tags when using [model profiles](../model-profiles-1/building-house-prices.md).

`raymon.Tag` objects have a `name`, a `value`, a `type` and, optionally, a `group`. The tag type can be any string you want (like ‘error’, ‘label’, ‘metric’), but some get a pretty color in the frontend. Tag groups are simply used to be able to group tags, e.g. all tags generated by a [model profile](../model-profiles-1/building-house-prices.md) will have the same tag group.

```python
from raymon import Tag

tags = [
    # Using a dict
    {
        "name": "client",
        "value": "bigshot_client",
        "type": "label"
    },
    # Using the Tag object
    Tag(name="sdk_version", value="1.4.2", type="label"),
    Tag(name="prediction_time_ms", value="120", type="metric")
]
trace.tag(tags)
```

### Logging Data

Raymon allows you to log data to the backend too. The data objects must have a reference (a name) that must be unique within the trace and which allows you to fetch the object from the backend later.

All data that is logged to the Raymon platform is serialised to JSON, so all data must be serialisable. Raymon offers data wrappers for popular data types that will take care of serialising your data in the `raymon.types` module. Of course, you can also define your own wrappers if you need them by implementing the `raymon.types.RaymonDataType` interface.

Logging data to a trace works as follows.

```python
import pandas as pd
import numpy as np
from PIL import Image

import raymon.types as rt


img = Image.open("./data_sample/castinginspection/def_front/cast_def_0_0.jpeg")
arr = np.array([[1, 2], [3, 4]])
df = pd.DataFrame(arr, columns=['a', 'b'])

trace.log(ref="native-ref", data=rt.Native(
    {"foo": "bar",
    "whatever": ["you", "want"],
    "all_native_types": 1}))
trace.log(ref="numpy-ref", data=rt.Numpy(arr))
trace.log(ref="pandas-ref", data=rt.DataFrame(df))
trace.log(ref="image-ref", data=rt.Image(img))
```

## Interacting with traces

### Web UI

After logging this data, you can navigate to the [web UI](https://ui.raymon.ai) and navigate to the Traces tab. There, you should see one trace, with 3 tags. When clicking on the eye icon, the trace should open and you should see the tags, text and data you have logged as shown below.

![Example of a very simple trace (without visualisations yet).](<../.gitbook/assets/image (11) (1).png>)

### API

You can fetch data from the backend for further debugging or analysis by clicking the download icon next to each data artefact, or download the complete trace by clicking the icon next to the Logs header.

For example, the code to fetch an object could look as follows:

```python
resp = api.object_search(project_id="d6ac1bf0-4e22-43ae-a85e-3cb2c1e5da80", trace_id="472b649d-cce8-4d50-9682-6b81a80755c0", ref="numpy-ref")

if not resp.ok:
    raise Exception("Something wrong.")

data = resp.json()
obj_id = data["obj_id"]
obj_data = data["obj_data"]

raymon_wrapped = rt.load_jcr(obj_data)
orig = raymon_wrapped.data
```

## Wrapping Up

This section provided a sneak peek into the Raymon backend, Web UI and API. More to come!