<p align="center">
  <img width="500"  src="./docsrc/assets/logo-blue-ai.png">
</p>

# Raymon: analyse data & model health

![Build](https://github.com/raymon-ai/raymon/workflows/test-build-deploy/badge.svg)
![Coverage](https://raw.githubusercontent.com/raymon-ai/raymon/master/coverage.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
<a href="https://github.com/raymon-ai/raymon/blob/master/LICENSE.md"><img alt="License" src="https://img.shields.io/github/license/raymon-ai/raymon"></a>
<a href="https://pypi.org/project/raymon/"><img alt="PyPI" src="https://img.shields.io/pypi/v/raymon"></a>
</p>

## What is Raymon?
Raymon helps Machine Learning teams analyse data, data health and model performance. 

Using data profiles, users can extract features describing data quality, data novelty, model confidence and prediction performance from data and use these features to validate production data and monitor for changes in data distributions, data health or model performance. 

Raymon is open source and can be used standalone but integrates nicely with the rest of the Raymon.ai ML Observability hub, for example to make models traceable and debuggable (link to tracing docs).

Raymon’s focus is on extractors that are cheap to compute and simple to understand. Currently, we offer extractors for structured data and vision data, but by implementing the right feature extractors we support any data type. Let us know if you would like to explore this!


## Docs
:point_right: https://docs.raymon.ai


## At a glance

### Installation

```bash
pip install raymon
```
### Building a model profile
Building a `ModelProfile` captures your expected model data characteristics...

```python
from raymon.profiling.extractors.structured import generate_components

profile = ModelProfile(
    name="HousePricesCheap",
    version="2.0.0",
    components=[
        InputComponent(name="feature_1", extractor=ElementExtractor(element="feature_1")),
        InputComponent(name="feature_2", extractor=ElementExtractor(element="feature_2")),
        InputComponent(name="feature_3", extractor=ElementExtractor(element="feature_3")),
        InputComponent(name="feature_4", extractor=ElementExtractor(element="feature_4")),               
        OutputComponent(name="prediction", extractor=ElementExtractor(element=0)),
        ActualComponent(name="actual", extractor=ElementExtractor(element=0)),
        EvalComponent(name="abs_error", extractor=AbsoluteRegressionError()),
    ],
    reducers=[
        MeanReducer(
            name="MAE",
            inputs=["abs_error"],
            preferences={"mean": "low"},
            results=None,
        )
    ],
)
profile.build(input=X, output=y_pred, actual=y_test)
profile.save(".")
```
### Validating production data
... and can then be used in production code to validate your incoming data and model performance monitoring.

```python
profile.validate_input(row)
profile.validate_outputs(prediction)
```
### Inspect and contrast model profiles
Raymon also lets you inspect and contrast profiles against each other.
![Profile contrast preview](docsrc/assets/profile-contrast.png)


### Logging text, data and tags

Moreover, Raymon makes model predictions debuggable by enabling you to log relevant text, data and tags from anywhere in your code. You can later use these tags and data objects to debug and improve your systems.

```python
import pandas as pd
import numpy as np
from PIL import Image

import raymon.types as rt
from raymon import Trace, RaymonAPILogger, Tag


logger = RaymonAPILogger(project_id=project_id)
trace = Trace(logger=logger, trace_id=None)

# Logging text messages
trace.info("You can log whatever you want here")

# Tagging traces
trace.tag([
        Tag(name="sdk_version", value="1.4.2", type="label"),
        Tag(name="prediction_time_ms", value="120", type="metric")
    ])

# Logging data
img = Image.open("./data_sample/castinginspection/def_front/cast_def_0_0.jpeg")
df = pd.DataFrame(arr, columns=['a', 'b'])

trace.log(ref="pandas-ref", data=rt.DataFrame(df))
trace.log(ref="image-ref", data=rt.Image(img))

```
For more information, check out our docs & examples!

