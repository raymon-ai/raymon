---
description: This page sets the scene for our use case.
---

# Use case description

To demonstrate Raymon, we'll use the use case and data of the [diabetic retinopathy detection Kaggle challenge](https://www.kaggle.com/c/diabetic-retinopathy-detection). Diabetic retinopathy is the leading cause of blindness in the working-age population of the developed world. It is estimated to affect over 93 million people. You are a data scientist responsible for building and maintaining a retinopathy detection service. This service ingests an image of a retina and must output the presence of diabetic retinopathy on a scale of 0 to 4.&#x20;

Reminder: all code used in this walkthrough can be found on Github. To get it, follow the instruction [here](intro-vision-walkthrough.md).

## Data description

The data for this use case can be found [here](https://github.com/raymon-ai/raymon-demos/tree/master/retinopathy/data). Some example input images are shown below. As mentioned before, the service's output is a number between 0 and 4.

![](../.gitbook/assets/997\_right.jpeg) ![](../.gitbook/assets/998\_left.jpeg) ![](../.gitbook/assets/998\_right.jpeg)

## The model

For your task you have of course trained a fancy model. Since the goal of this walkthrough has nothing to do with model training and since computer vision models can be quite large and time consuming to train, we'll mock out the model. You can find the code in [`models.py`](https://github.com/raymon-ai/raymon-demos/blob/master/retinopathy/retinopathy/models.py), together with the code for an oracle that can be used to look up the correct prediction for an image.

```python
import pandas as pd
import random


class RetinopathyMockModel:
    def __init__(self, oracle):
        self.oracle = oracle

    def predict(self, data, metadata, p_corr):
        iscorr = random.random() <= p_corr
        target = self.oracle.get_target(metadata)
        if iscorr:
            pred = target
        else:
            choices = {0, 1, 2, 3, 4}
            choices = choices.difference({target})
            pred = random.choice(list(choices))
        return pred

    def train(self, data):
        pass


class ModelOracle:
    def __init__(self, labelpath):
        self.labels = pd.read_csv(labelpath)

    def get_src(self, metadata):
        for tag in metadata:
            if tag["name"] == "srcfile":
                return tag["value"]

    def get_target(self, metadata):
        srcfile = self.get_src(metadata)
        return int(self.labels.loc[self.labels["image"] == srcfile, "level"].values[0])
```

As you can see, the oracle always returns the correct prediction when the `get_target` method is called, and the `RetinopathyMockModel` returns a correct prediction with a probability `p_corr`, which is passed when calling the `predict` method.

Calling the model and oracle goes as follows:

```python
import uuid
from PIL import Image

from const import TAG_CHOICES, BAD_MACHINE, ROOT, SECRET, LABELPATH
from models import RetinopathyMockModel, ModelOracle


idx = 0
files = list((ROOT / "data/1").glob("*.jpeg"))
trace_id = str(uuid.uuid4())
imgpath = files[idx]
img = Image.open(imgpath)
metadata = [{"name": "srcfile", "value": imgpath.stem, "type": "label"}]

oracle = ModelOracle(labelpath=LABELPATH)
model = RetinopathyMockModel(oracle=oracle)
model.predict(data=img, metadata=metadata, p_corr=0.95)
oracle.get_target(metadata=metadata)
```

## The deployment

Raymon's focus is post-deployment, so let's set up a toy deployment and set up code to push data through it!&#x20;

The following code (which can also be found [here](https://github.com/raymon-ai/raymon-demos/blob/master/retinopathy/retinopathy/base.py)) sets up our toy deployment. It does the following things:

1. It defines a RetinopathyDeployment that ingests data and makes a prediction. (line 12)
2. It pushes data through the deployment (line 70, or the `run` method at line 44).
   1. Generate a request id, which we call `trace_id`
   2. get some metadata for this request like the age of the patient, the hospital that generated the data, the machine id that generated the data.&#x20;
   3. Load the image
   4. Process it.



```python
import os
import random
import uuid
import traceback
import pendulum
from PIL import Image

from models import ModelOracle, RetinopathyMockModel
from const import TAG_CHOICES, BAD_MACHINE, ROOT, SECRET, LABELPATH


class RetinopathyDeployment:
    def __init__(self, version, model):
        self.version = version
        self.model = model

    def process(self, trace_id, data, metadata, p_corr):
        try:
            resized_img = data.resize((512, 512))
            pred = self.model.predict(resized_img, metadata, p_corr=p_corr)
            print(f"Processed trace {trace_id}. Prediction: {pred}")
            return pred
        except Exception as exc:
            print(traceback.format_exc())


def pick_tags(TAG_CHOICES):
    tags = []
    for key in ["age", "hospital", "eye"]:
        value = random.choice(TAG_CHOICES[key])
        tags.append({"name": key, "value": value, "type": "label"})
        if key == "hospital":
            machine_id = random.choice(TAG_CHOICES["machine_id"][value])
            tags.append({"name": "machine_id", "value": machine_id, "type": "label"})
    return tags


def get_machine(metadata):
    for tag in metadata:
        if tag["name"] == "machine_id":
            return tag["value"]


def run():
    for i in range(N_RAYS):
        trace_id = str(uuid.uuid4())
        metadata = pick_tags(TAG_CHOICES)
        idx = i % len(files)
        imgpath = files[idx]
        metadata.append({"name": "srcfile", "value": imgpath.stem, "type": "label"})
        img = Image.open(imgpath)
        img.thumbnail(size=(500, 500))
        p_corr = 0.95
        pred = deployment.process(
            trace_id=trace_id, data=img, metadata=metadata, p_corr=p_corr
        )


#%%
N_RAYS = int(os.environ.get("RAYMON_N_RAYS", 100))
VERSION = "retinopathy@3.0.0"

files = list((ROOT / "data/1").glob("*.jpeg"))
model_oracle = ModelOracle(labelpath=LABELPATH)
model = RetinopathyMockModel(oracle=model_oracle)
deployment = RetinopathyDeployment(version=VERSION, model=model)


start_ts = pendulum.now()
trace_ids = run()
end_ts = pendulum.now()
print(f"Start: {str(start_ts.in_tz('utc'))}, End: {str(end_ts.in_tz('utc'))}")
```

You should be able to run this file by executing the following command from the `raymon-demos/retinopathy/retinopathy` working directory.

```
python base.py
```

## Wrapping up

Allright, we have data, a model and a deployment. Now it's time to see what Raymon can bring to the table!

