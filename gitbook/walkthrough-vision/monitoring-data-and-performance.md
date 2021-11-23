---
description: >-
  This section illustrates how you can easily set up data & model performance
  monitoring.
---

# Monitoring Data & Performance

## ModelProfiles

Monitoring of data and model performance use ModelProfiles that are introduced [here](../model-profiles-1/building-computer-vision.md). ModelProfiles are in essence an easy way to extract data & model metrics from model predictions, configure those extractors in a single artefact as code, and set up data-centric monitoring in Raymon.

## A basic profile

To set up data monitoring, let's create a basic profile. The full code for this can be found [here](https://github.com/raymon-ai/raymon-demos/blob/master/retinopathy/retinopathy/train\_base.py).

```python
loaded_data, metadata = load_data(dpath=DATA_PATH, lim=LIM)
preds, targets = get_preds_actuals(metadata, loaded_data)

profile = ModelProfile(
    name="retinopathy",
    version="3.0.0",
    components=[
        InputComponent(
            name="sharpness",
            extractor=Sharpness(),
            dtype=DataType.FLOAT,
        ),
        InputComponent(
            name="intensity",
            extractor=AvgIntensity(),
            dtype=DataType.FLOAT,
        ),
        InputComponent(
            name="outlierscore",
            extractor=DN2AnomalyScorer(k=20),
            dtype=DataType.FLOAT,
        ),
        OutputComponent(
            "model_prediction", extractor=ElementExtractor(0), dtype=DataType.INT
        ),
    ],
)


profile.build(input=loaded_data, output=preds, actual=None, silent=False)
profile.view()
profile.save(".")
```

By analysing the code above, you see that our simple profile extracts 3 metrics from the input: the sharpness of the image, the images average intensity and an outlier score for the image. It also extracts a feature from the output, the feature being the prediction itself (i.e. a number between 0 and 4).

Line 30 builds the profile based on a sample of data. This data should be the same data (or a subset) of the data your model is trained on. The model profile will build the extractors if necessary  (like for the DN2AnomalyScorer), use the extractors to extract metrics from the data and save the distributions of those metrics. As such, the profile profiles your data.

As shown earlier, the profiles can be used to assess the health of your production data. Things like blurry images, images with bad lighting or images that are very dissimilar to the training set should raise warnings in your production system. This is exactly what raymon does!

## Using the profile

Let's now integrate the profile in the deployment! As always, we have written some example code for this which can be found [here](https://github.com/raymon-ai/raymon-demos/blob/master/retinopathy/retinopathy/base\_basic\_profile.py). Let's inspect the relevant parts.

```python
class RetinopathyDeployment:
    def __init__(self, version, model, profile):
        self.version = version
        self.model = model
        self.raymon = RaymonAPILogger(
            url=RAYMON_URL,
            project_id=PROJECT_ID,
            batch_size=20,
        )
        self.profile = profile

    def process(self, trace_id, data, metadata, p_corr):
        trace = Trace(logger=self.raymon, trace_id=trace_id)
        trace.tag(metadata)
        try:
            trace.log(ref="request_data", data=rt.Image(data))
            tags = self.profile.validate_input(data)
            trace.tag(tags)
            resized_img = data.resize((512, 512))
            trace.log(ref="resized_data", data=rt.Image(resized_img))
            pred = self.model.predict(resized_img, metadata, p_corr=p_corr)
            print(f"Processed trace {trace_id}. Prediction: {pred}")
            trace.tag(self.profile.validate_output([pred]))
            return pred
        except Exception as exc:
            print(traceback.format_exc())
            trace.tag(
                [{"type": "err", "name": "Processing Exception", "value": str(exc)}]
            )
        finally:
            trace.logger.flush()
```

As you can see, we've added the profile to the deployment (line 2, line 10) and use it to validate our incoming and outgoing data (lines 17, 18, and line 23. More info about data validation can be found [here](../model-profiles-1/validating-data.md).

After running the code as follows, we see a lot more tags in the traces view. All these tags can be used to monitor or slice monitoring and dashboards in Raymon!

```bash
python base_basicprofile.py
```

![There are a lot more tags in Raymon already!](<../.gitbook/assets/image (16).png>)

## Expanding the profile a bit

Before continuing, we'll extend the setup and profile a bit. First of all, we'll assume we have feedback coming in some time after we've made a prediction. In this case, the feedback will be the actuals. We'll then see how we can easily plug this into Raymon.

First, let's adapt our profile. Full code [here](https://github.com/raymon-ai/raymon-demos/blob/master/retinopathy/retinopathy/train\_actuals.py). As can be seen below, since we have the actual in production, we can add it to our model profile (line 23). Additionally, we can combine the output and actual into evaluation metrics, that we can also add to our model profile. Examples of those metrics are the absolute error of our prediction, or the error type of our prediction if we pose the retinopathy detection as a classification problem, as shown in lines 26-35). This will set up monitoring for error magnitude for example. Lastly, we can use those evaluation metrics to calculate averaged scores, like mean absolute error, precision and recall, as shown in lines 37 and below.&#x20;

```python
profile = ModelProfile(
    name="retinopathy",
    version="3.0.0",
    components=[
        InputComponent(
            name="sharpness",
            extractor=Sharpness(),
            dtype=DataType.FLOAT,
        ),
        InputComponent(
            name="intensity",
            extractor=AvgIntensity(),
            dtype=DataType.FLOAT,
        ),
        InputComponent(
            name="outlierscore",
            extractor=DN2AnomalyScorer(k=20),
            dtype=DataType.FLOAT,
        ),
        OutputComponent(
            "model_prediction", extractor=ElementExtractor(0), dtype=DataType.INT
        ),
        ActualComponent(
            "model_actual", extractor=ElementExtractor(0), dtype=DataType.INT
        ),
        EvalComponent(
            "regression_error",
            extractor=AbsoluteRegressionError(),
            dtype=DataType.FLOAT,
        ),
        EvalComponent(
            "classification_error",
            extractor=ClassificationErrorType(positive=0),
            dtype=DataType.CAT,
        ),
    ],
    scores=[
        MeanScore(
            name="mean_absolute_error",
            inputs=["regression_error"],
            preference="low",
        ),
        PrecisionScore(
            name="precision",
            inputs=["classification_error"],
        ),
        RecallScore(
            name="recall",
            inputs=["classification_error"],
        ),
    ],
)


profile.build(input=loaded_data, output=preds, actual=targets, silent=False)
profile.view()
```

Secondly, let's inspect the new deployment code. Full code [here](https://github.com/raymon-ai/raymon-demos/blob/master/retinopathy/retinopathy/base\_raymon\_actuals.py). The most relevant part is the one where we get an actual, validate it, and log it and its validation tags to Raymon.

```python
class FeedbackDeployment:
    def __init__(self, model_oracle):
        self.raymon = RaymonAPILogger(
            url=RAYMON_URL,
            project_id=PROJECT_ID,
            auth_path=SECRET,
            batch_size=20,
        )
        self.model_oracle = model_oracle
        self.profile = profile

    def process(self, trace_id, metadata):
        trace = Trace(logger=self.raymon, trace_id=str(trace_id))
        target = self.model_oracle.get_target(metadata)
        trace.log(ref="actual", data=rt.Native(target))
        trace.tag(profile.validate_actual(actual=[target]))
        trace.logger.flush()
        return target
```

To run the new code:

```bash
python base_raymon_actuals.py
```

Now, in this extended setup we have more data in Raymon, among which the prediction and the actual. This opens some new possibilities...



## Configuring Raymon

Before continuing, we should upload the model profile we've trained to Raymon. This is done as follows:

```python
from raymon import ModelProfile
from raymon import RaymonAPI

api = RaymonAPI(url=f"https://api.raymon.ai/v0")

schema = ModelProfile.load("path_to_your_profile.json")
resp = api.profile_create(project_id="<your profile id>", profile=schema)
resp.json()
```

Next, we should let Raymon know that we want to set up monitoring using this profile. For that, we need to edit the manifest and add a [reducer](../actions/reducers.md) action of type `profile_reducer`_ _with the same name as our profile's identifier (`profile_name@version`). Lastly, we need to specify the interval (in minutes) that needs to elapse between data checks. For example, if we want to check our data every 10 minutes, we set `reducer_interval_m `to` 10.`

```yaml
project_id: retinopathy

actions:
  visualize:
    - name: show_request_data
      function: img2html
      inputs:
        data: request_data
      params: null
    - name: show_resized_data
      function: img2html
      inputs:
        data: resized_data
      params: null

  reduce:
    - reducer_type: profile_reducer
      name: retinopathy@3.0.0
      reducer_interval_m: 10
```

Actually, now that we're changing the manifest anyway, let's add a mapper as well. We already mentioned that having the model output and actual in Raymon has certain advantages. Indeed, we can combine both on the Raymon platform and automatically calculate all the evaluation metrics and scores specified in the ModelProfile. For this, all we need to do is add a [mapper](../actions/mappers.md) to the actions as shown below.

```yaml
  actions:
    map:
    - name: profile_eval
      mapper_type: profile_eval
      profile: retinopathy@3.0.0
      inputs:
        output: model_prediction # Ref
        actual: actual
```

Don't forget to apply the new manifest!

```python
from raymon import RaymonAPI

with open("../manifest.yaml", "r") as f:
    cfg = f.read()
api = RaymonAPI(url=f"https://api.raymon.ai/v0")
resp = api.orchestration_apply(
    project_id="4854ecdf-725e-4627-8600-4dadf1588072", cfg=cfg
)
resp
```



## Wrap-up

In this section we've seen how to integrate data validation using model profiles, and have set up data processing using actions. Before checking the results of this on the Raymon platform, lets read through the next section. There, we'll push some more data after configuring the monitoring a bit more. Head over there!
