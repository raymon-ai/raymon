# Visualisations

## Native Actions

```yaml
actions:
  visualize: # On demand
    - name: show_normalized_data
      function: img2html
      inputs:
        data: flipped_data # Peephole name
      params: null
```

## Webhook Actions

### AWS Lambda

```yaml
actions:
  visualize: # On demand
    - name: request_data_lambda
      visual_type: lambda_hook
      function: img2html
      inputs:
        data: request_data # Ref
      settings:
        aws_access_key_id: <your key id>
        aws_secret_access_key: <your secret access key>
        aws_region: eu-central-1
```
