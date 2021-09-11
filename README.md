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
**Raymon helps Machine Learning teams analyse data, data health and model performance**. Using Raymon, users can extract features describing data quality, data novelty, model confidence and prediction performance from model predictions. Then, they can use these features to validate production data and monitor for data drift, data degradation and model degradation. 

**We can support any data type**. Currently, we offer extractors for structured data and vision data, but you can easily implement your own extractor which means we can any data type and any extractor that you want. 

**Raymon’s focus is on simplicity, practicality and extendability**. We offer a set of extractors that are cheap to compute and simple to understand. 

**Raymon is open source and can be used standalone** but integrates nicely with the rest of the Raymon.ai ML Observability hub, for example to make predictions traceable and debuggable.

## Quick Links
- :point_right: [Docs](https://docs.raymon.ai)
- :point_right: [Examples](./examples)
- :point_right: [Issues](https://github.com/raymon-ai/raymon/issues)


## At a glance

### Installation

```bash
pip install raymon
```
### Building a model profile
Building a `ModelProfile` captures all kinds of data characteristics of your models inputs, outputs, actuals and predictions.

```python
profile = ModelProfile(
    name="HousePricesCheap",
    version="3.0.0",
    components=[
        InputComponent(
            name="outlier_score",
            extractor=SequenceSimpleExtractor(
                prep=coltf, extractor=KMeansOutlierScorer()),
        ),
        OutputComponent(name="prediction", extractor=ElementExtractor(element=0)),
        ActualComponent(name="actual", extractor=ElementExtractor(element=0)),
        EvalComponent(name="abs_error", extractor=AbsoluteRegressionError()),
    ] + generate_components(X_train[feature_selector].dtypes, 
                            complass=InputComponent),
    scores=[
        MeanScore(
            name="MAE",
            inputs=["abs_error"],
            preference="low",
        ),
        MeanScore(
            name="mean_outlier_score",
            inputs=["outlier_score"],
            preference="low",
        ),
    ],
)
profile.build(input=X_val[feature_selector], 
              output=y_pred_val[:, None], 
              actual=y_val[:, None])
```
### Validating production data
Profiles can then be used in production code to validate your incoming data and model performance monitoring.

```python
tags = profile.validate_input(request)
output_tags = profile.validate_output(request_pred)
actual_tags = profile.validate_actual(request_actual)
eval_tags = profile.validate_eval(output=request_pred, 
                                  actual=request_actual)
# or all at once:
all_tags = profile.validate_all(input=request, 
                                output=request_pred, 
                                actual=request_actual)
```

### Inspect and contrast model profiles
interactive-demo

https://user-images.githubusercontent.com/7951058/132864346-2715fb47-00e9-484c-9f06-c709d4a9847f.mov




### Logging text, data and tags

Moreover, if you want to use the rest of the platform, Raymon makes model predictions traceable and debuggable. Raymon enables you to log text, data and tags from anywhere in your code. You can later use these tags and data objects to debug and improve your systems.

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

