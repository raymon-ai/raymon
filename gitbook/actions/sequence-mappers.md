# Sequence Mappers

## Native sequence mappers

Currently, there are none.

## Webhook Sequence Mappers

### AWS Lambda

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
