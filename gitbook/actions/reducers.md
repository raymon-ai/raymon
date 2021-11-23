# Reducers

## Native Reducers

### Profile Reducers

```yaml
actions:
  reduce:
    - reducer_type: profile_reducer . # Indicate that this is a profile reducer
      name: retinopathy@3.0.0 # The name needs to match the profile identifier
      reducer_interval_m: 10 # Execute this reducer every 10 minutes
```

## Webhook Reducers

There is no support for this since reducers require direct database access.
