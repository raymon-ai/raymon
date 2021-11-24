---
description: Introducing Actions.
---

# Intro

Raymon helps you analyse and monitor deployed AI systems. Since AI has countless different use cases and data types, it is impossible for Raymon to offer all data processing operations out-of-the-box. Often times, Data Scientists will want to plug in a certain operation and use its results in Raymon. This is what actions are for: they allow you to easily extend Raymon.

There are various types of actions. There are visualisations, mappers, reducers, alerts and a few more. Some of those types allow you to specify your own function (e.g. an AWS Lambda function) that will be called by Raymon once a certain event occurs.&#x20;

### Creating a manifest

Actions are configured through the project manifest yaml file. A project manifest may look like this:

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

  reduce:
    - reducer_type: profile_reducer
      name: retinopathy@3.0.0
      reducer_interval_m: 10

  map:
    - name: profile_eval
      mapper_type: profile_eval
      profile: retinopathy@3.0.0
      inputs:
        output: model_prediction # Ref
        actual: actual

slices:
  - space:
      - tag: machine_id

```

We'll dig deeper into the actions in the following sections.

### Applying the manifest

After creating a manifest file, you need to apply it to your project as follows:

```python
from raymon import RaymonAPI

with open("manifest.yaml", "r") as f:
    cfg = f.read()
api = RaymonAPI(url=f"https://api.raymon.ai/v0")
resp = api.orchestration_apply(
    project_id="<your project id>", cfg=cfg
)
resp
```

Now, let's discuss the action types in more detail!
