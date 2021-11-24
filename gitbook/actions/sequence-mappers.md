---
description: Sequence mapper allow you to process sequences of objects.
---

# Sequence Mappers

Even if your model makes predictions on individual datums, like images, it might be useful to analyse successive predictions coming fro ma certain source. For example, when detecting objects in an image, detection flicker in successive images [indicates poor model performance](https://arxiv.org/abs/2003.01668). Knowing this will help you sample valuable data for model retraining. This is what sequence mappers help you do.&#x20;

Sequence mappers are mappers that are called on a sequence of traces. For example, in the [retinopathy detection use case](../walkthrough-vision/intro-vision-walkthrough.md), every machine generates a sequence of data. Therefore, if we slice the data on `machine_id`, we'll get sequences for every machine.

## Native sequence mappers

Currently, there are none.

## Web Hook Sequence Mappers

Currently, we only support AWS Lambda, but other FaaS platforms can and will  be supported too. [Do not be shy to let us know what integrations you are missing](https://github.com/raymon-ai/raymon/issues)!

### AWS Lambda

Plugging in a sequence mapper implemented as a lambda function, insert something like the snippet below in your action manifest.

```yaml
actions: 
  sequence_map:
    - name: camera_sequence
      seq_mapper_type: lambda_hook
      function: dummy-seqmapper
      sequence_def:
        - space:
            - tag: machine_id
      settings:
        aws_access_key_id: <aws_access_key_id>
        aws_secret_access_key: <aws_secret_access_key>
        aws_region: eu-central-1
      sequence_interval_m: 1
      sequence_lim: 20
      inputs:
        flipped_data: flipped_data # param_name: ref
        request_data: request_data

```

Some notes:

* The `sequence_def` (line 6 - 8) defines the slice that defines a sequence of data.&#x20;
* `sequence_interval_m` (line 13) specifies the interval between calls to the sequence mapper
* `sequence_lim` (line 14) determines the max number of traces a sequence should contain.&#x20;
* AWS Lambda functions currently have a request limit of 6 MB.

### Writing your own

Writing your own function is similar as for mappers.&#x20;

```python
import pendulum

def dummy_mapper(event, context):
    slicestr = event["slicestr"]
    begin = pendulum.parse(event["begin"])
    data = event["data"]
    
    resp = {}
    
    for trace_id, trace_data in data.items():
        print(trace_id)
        print(trace_data)
        resp[trace_id] = [{
            "name": "sequence",
            "value": f"{slicestr}-{begin}",
            "type": "label",
            "group": "seq_mapper"
        },
        ]
    return resp

```

Some notes:

* `data` (line 6) will be a dictionary containing the trace ids as keys, each having a value that is another dict, just like with normal [mappers](mappers.md).
* Your function should return a dict containing the trace ids as keys, each having a list of [tags](../using-the-raymon-hub/tags.md) as value. These tags will then be attached to the specified trace.

