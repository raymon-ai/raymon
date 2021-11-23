---
description: >-
  In this section we'll see how to set up slice-based monitoring and how to tune
  alerts.
---

# Slice-based monitoring

## Adding slices

So far, we have set up data inspection and monitoring capabilities. There is one more thing we'd like to touch here though: slice-based monitoring. In AI projects, you often process data from different subsets of clients. For example, in our use case, we're processing data from multiple hospitals, multiple machines, multiple age groups, multiple sexes, multiple ethnicities, etc... You probably want to be sure you're treating all end users fairly right? And if you are not, at least you want to know about it. Slice-based monitoring helps you ensure this.

By adding slices to the manifest, all monitoring will be done not only globally, but also for the slices specified. As an example, lets set up monitoring for all machine\_ids. This is very easy. Just add this to the manifest:

```json
slices:
  - space:
      - tag: machine_id
```

That's it? Yes, that's it. What this does is tell Raymon to slice production data on the `machine_id` tag's values, and benchmark all slices against each other. If one machine generates faulty data, resulting in lower data quality and performance, you will be notified about it.

Of course, we can specify much more slices. For more info, see [slices](../using-the-raymon-hub/slices.md).

As a reminder, the complete manifest now looks as follows.&#x20;

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

Do not forget to apply this new configuration!

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

## Pushing more data

Allright, now that we have everything set up, we can push more data. Remember we have the monitoring interval set up for 10 minutes, so we need to let our code run for a while. Uploading data to Raymon from your local machine can be quite slow, so we do not recommend lowering the interval. We need sufficient data in the reducer interval to avoid overly sensitive alerts.

Let's push 2000 traces. That should keep up going for a while:

```bash
RAYMON_N_TRACES=2000 python base_raymon_actuals.py
```

## Wrap-up

While we're waiting for our run to last at least 10 minutes, let's wrap up. Using slices, we can easily watch subsets of data for regressions. In the next section, we'll see what kind of alerts we get out of Raymon and how we can tune those.

