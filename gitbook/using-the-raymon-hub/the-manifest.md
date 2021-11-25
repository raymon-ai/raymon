---
description: >-
  The project manifest allows you to configure the Raymon platform for your
  project.
---

# The Manifest

### Creating a manifest

The project manifest allows you to configure the Raymon platform for your project. For example, [actions](broken-reference) and [slices](slices.md) are configured through the project manifest. The manifest is a yaml file, generally called `manifest.yaml` in the docs and example code). A project manifest may look like this:

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

### Applying the manifest

After creating or updating a manifest file, you need to apply it to your project as follows:

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
