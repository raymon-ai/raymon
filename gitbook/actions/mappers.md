# Mappers

## Native Mappers

### ModelProfile mappers

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

## Webhook Mappers

### AWS Lambda

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
