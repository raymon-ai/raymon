---
description: Visualisations let you... visualise data.
---

# Visualisations

One of the functionalities Raymon offers is inspecting the trace view. Traces consist of all the objects, tags and info messages logged to Raymon. Often, it is very useful to set up visualisations using some of those objects for easy data inspection in your production system. The most straightforward use case could be to visualise an image or pandas dataframe. More advanced use cases visualisations visualisations that offer explainability into model predictions.

Visualisation actions for a certain trace are only triggered when someone access that trace or requests a visual for that trace in some other way. They are not executed automatically for all traces that are received in Raymon, like some other actions are.

## Native Actions

Raymon currently offers very basic native visualisation actions: one for visualising images, one to visualise native types and one for visualising pandas dataframes and series. They are configured as follows.

### Image visualisation

To visualise an image, you first need to log an image to Raymon (which must be of the type `rt.Image`) like this:

```python
from raymon import types as rt

trace.log(ref="request_data", data=rt.Image(data))
```

Then, one can configure an action to visualise this image as follows.

```yaml
actions:
  visualize:
    - name: show_request_data
      function: img2html
      inputs:
        data: request_data
```

Line 4 defines the function to call whenever this action is triggered. Since this is a native action, this is a function that is shipped with Raymon. Lines 5 and 6 define the inputs for the function. In this case, the function will be called with one parameter (called `data`, and its value will be the object logged with reference `request_data` for the trace this action is triggered for.

### Pandas visualisation

This is very similar the the image visualisation described above, but the configuration is of course slightly different.

Logging goes like this:

```python
trace.log(ref="request_data", data=rt.Series(data))
trace.log(ref="preprocessed_input", data=rt.DataFrame(prep_df))
```

Specifying a visualisation action is done as follows.

```yaml
actions:
  visualize: # On demand
    - name: request_data
      function: pandas2html
      inputs:
        data: request_data
      params: null
```

### Native types visualisations

For visualisation of native Python types first log one like this:

```python
trace.log(ref="model_prediction", data=rt.Native(pred))
```

Then, visualise it like this.

```yaml
    - name: show_pred
        data: model_prediction
      params: null
```

## Web Hook Actions

As mentioned before, the native supported visualisation actions are very simple. For your use case, you may want something more complex. This is possible by writing your own function, deploying it on (for example) AWS Lambda and plugging it into Raymon. Other FaaS platforms can and will  be supported too in the future (Google Cloud Functions, OpenFaas,..). [Do not be shy to let us know what integrations you are missing](https://github.com/raymon-ai/raymon/issues)!

### AWS Lambda

Setting up a lambda function goes as follows. Note the `visual_type`_ (_`lambda_hook`), and the settings.

```yaml
actions:
  visualize:
    - name: request_data_lambda
      visual_type: lambda_hook
      function: img2html
      inputs:
        data: request_data # Ref
      settings:
        aws_access_key_id: <your key id>
        aws_secret_access_key: <your secret access key>
        aws_region: <your aws region>
```

### Writing your own action

To be able to write and deploy your own function, you need to know what to program right? The snippet below shows what a function can look like. In this case, it's a Lambda function. It receives a parameter 'event' which contains a dict. This dict will contain a key, value pair for every input specified in the action definition. The key will be the name specified (here: '`data`'), and the value will be the object artefact, in a JSON-compatible format ("jcr"). This can then be loaded as shown on lines 2 and 3.

Your function should return a str, containing HTML. This HTML will be rendered in the UI. Thats it!

```python
import raymon.types as rt

def img2html(event, context):
    data = event["data"]
    img = rt.load_jcr(data)
    if isinstance(img, rt.Image):
        pilimg = img.data
    else:
        raise TypeError(f"Unsupported input type: {type(img)}")
    htmlstr = pil2html(pilimg)
    return htmlstr

```

