# Mappers

Mapper actions allow you to do some processing on logged artefacts. Mappers can convert one or multiple inputs into tags that are useful for Raymon. One useful thing you can do with mappers is combine a model prediction and an actual you receive some time later into an error metric for that model prediction.

Unlike visualisations, mappers are executed for all traces automatically. When Raymon receives an object with reference '`ref`', it will check all mappers that have reference `ref` as an input. If all inputs for that mapper are available in Raymon, it will execute the mapper and store the resulting tags for that trace.

## Native Mappers

### ModelProfile mappers

By logging objects to Raymon from different services, for example logging the model prediction from your deployment and logging the actual from a human-in-the-loop that annotates a sample of production data, Raymon has access to both objects. It can then combine those object into performance metrics. This is possible by writing a custom mapper (see below), or you can use a mapper specific for ModelProfiles like shown below. This mapper will combine the model prediction and the actual into the performance metrics specified in the profile.

```yaml
actions:
  map:
    - name: profile_eval
      mapper_type: profile_eval
      profile: retinopathy@3.0.0
      inputs:
        output: model_prediction
        actual: actual
 
```

## Web Hook Mappers

Next to native mappers, it's possible to write your own. That way, you can do any computation you like on any combination of objects.

### AWS Lambda

Setting up an AWS Lambda action is done as follows.

```yaml
actions:
  map:
    - name: dummy_aws_hook
      mapper_type: lambda_hook
      function: dummy-mapper
      settings:
        aws_access_key_id: <aws_access_key_id>
        aws_secret_access_key: <aws_secret_access_key>
        aws_region: eu-central-1
      inputs:
        data: request_data 
```

### Writing your own

The snippet below illustrates what a mapper function can look like. In this case, it's a Lambda function. It receives a parameter 'event' which contains a dict. This dict will contain a key, value pair for every input specified in the action definition. The key will be the name specified (here: '`data`'), and the value will be the object artefact, in a JSON-compatible format ("jcr"). This can then be loaded as shown on lines 2 and 3.

Your function should return a list containing Raymon tags.

```python
import raymon.types as rt

def dummy_mapper(event, context):
    img = rt.load_jcr(event["data"])

    return [{
        "name": "lambda_tag",
        "value": 1.4,
        "type": "label",
        "group": "dummy"
    },
    {
        "name": "lambda_tag_2",
        "value": "text",
        "type": "label",
        "group": "dummy"
    }]

```

