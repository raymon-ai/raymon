---
description: >-
  This section outlines how to set up a Raymon project, send data to it, and how
  to use Raymon for data inspection and data fetching.
---

# Integrating Raymon

## Creating a project

Before sending data to Raymon, you'll need to create a project to send data to. For this, go to [https://raymon.app/](https://raymon.app), login and click the "New Project" button. After entering a name for your project and clicking "continue". You should now see your project listed.

![](<../.gitbook/assets/image (21) (1).png>)

The uuid at the top right of the box is your project id. You need to copy this id to you clipboard.

## Sending data to the project

Sending data to Raymon is done as explained in [tracing predictions](../using-the-raymon-hub/untitled.md). Have a read through that section if you have not done this before.

For our use case, we will add some logging to our deployment to help us and our future colleagues validate whether our systems still functions properly using Raymon traces. Additionally, we will enrich these traces with extra metadata that we can use to set up monitoring later.&#x20;

Let's consider the code below. It's the same code as before, but we've added some logging. As always, the full code is on Github and can be found [here](https://github.com/raymon-ai/raymon-demos/blob/master/retinopathy/retinopathy/base\_tracing.py).

```python
class RetinopathyDeployment:
    def __init__(self, version, model):
        self.version = version
        self.model = model
        self.raymon = RaymonAPILogger(
            url=RAYMON_URL,
            project_id=PROJECT_ID,
            batch_size=20,
        )

    def process(self, trace_id, data, metadata, p_corr):
        trace = Trace(logger=self.raymon, trace_id=trace_id)
        trace.tag(metadata)
        try:
            trace.log(ref="request_data", data=rt.Image(data))
            resized_img = data.resize((512, 512))
            trace.log(ref="resized_data", data=rt.Image(resized_img))
            pred = self.model.predict(resized_img, metadata, p_corr=p_corr)
            print(f"Processed trace {trace_id}. Prediction: {pred}")
            return pred
        except Exception as exc:
            print(traceback.format_exc())
            trace.tag(
                [{"type": "err", "name": "Processing Exception", "value": str(exc)}]
            )
        finally:
            trace.logger.flush()

```

Notice lines 5, 12, 13, 15, 17 and 27. What happened there?

* Line 5: our deployment keeps a reference to the Raymon API, which is used to send data to it. Here, the `RAYMON_URL` is set to the default one (`ttps://api.raymon.ai/v0)`, `PROJECT_ID` should be your project id that you copied above and `batch_size=20 `indicates that we want to send data to Raymon in batches of 20.
* Line 12: We create a trace object that acts as a logger. All data logged to this object will be sent to Raymon and connected to the same trace.&#x20;
* Line 13: Let's tag the trace with all the metadata that we have. Remember, the metadata in this case are things like the hospital sending the data, the machine id that took the picture, the age of the patient and so on. We will be able to use all this metadata to slice and dice our production data!
* Line 15 and 17: log images to Raymon.&#x20;
* Line 27: makes sure all data is sent to Raymon and the buffer is empty.

### Trying it out

You can execute this code by running the following command from the `raymon-demos/retinopathy/retinopathy` working directory.

```bash
python base_tracing.py 
```

When running the script, look for the following lines to make sure all data is being send and received correctly:

```bash
2021-11-23 10:59:30,330 - Raymon - None - Posted buffer. Status: OK
```

Now, you can go to the Raymon UI, click on your project and navigate toward the traces view. There, you should now see the some traces. By clicking on the eye icon you can see the expanded view.

## Configuring the project

We have pushed some data, but inspecting this data in the Trace view is not exactly useful. To improve this, we can configure visualisations using actions as described in [Visualisations](../actions/visualisations.md).

Let's define a native visualisation for the images that we have logged. To do this, create a `manifest.yaml `file and paste the following contents:

```yaml
project_id: retinopathy

actions:
  visualize:
    - name: show_request_data
      function: img2html
      inputs:
        data: request_data
    - name: show_resized_data
      function: img2html
      inputs:
        data: resized_data

```

Now, upload it to Raymon:

```python
from raymon import RaymonAPI

with open("manifest.yaml", "r") as f:
    cfg = f.read()
api = RaymonAPI()
resp = api.orchestration_apply(
    project_id="<your project id>", cfg=cfg
)
resp
```

Now, the manifest should be visible on the settings page. Moreover, when opening the trace detail view again on the traces page, you should see some visualisations!

![](<../.gitbook/assets/image (20).png>)

The actions that we've set up here are of course very simple ones, but remember actions are very versatile. For example, they can take multiple logged object as input and support webhooks, so you can easily create very complex visualisations that may help you gain more insight in your models!

## Wrapping up

In this section, we have seen how we can integrate Raymon for simple data logging and inspection. Head over to the next section to set up data and model performance monitoring.
