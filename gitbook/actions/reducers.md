# Reducers

Reducers are actions that are triggered every x minutes, aggregate data (tags), perform checks resulting in issues and write those issues back to Raymon. These issues are then shown on the issues page if applicable. Reducers power Raymon's monitoring capabilities.

## Native Reducers



### Profile Reducers

As already mentioned before, setting up monitoring for data quality, drift and model performance is done using a ModelProfile. Configuring this works like this:

```yaml
actions:
  reduce:
    - reducer_type: profile_reducer . # Indicate that this is a profile reducer
      name: retinopathy@3.0.0 # The name needs to match the profile identifier
      reducer_interval_m: 10 # Execute this reducer every 10 minutes
```

Note: reducers work together with [slices](../using-the-raymon-hub/slices.md)! Read more [here](../walkthrough-vision/slice-based-monitoring.md).

## Web Hook Reducers

There is no support for this since reducers require direct database access.
