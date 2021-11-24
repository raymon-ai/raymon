# Alerts

When Raymon's [reducers](reducers.md) detect issues, you may want to be alerted. This is possible by configuring alert actions.&#x20;

## Web Hooks Alerts

Alerts are always implemented through calling some apps web hook.

### Slack

Slack allows apps to post messages to certain channels. You can set up Raymon to post a message to your slack channel when it has detected an issue. To get your slack incoming web hook, read [this](https://slack.com/help/articles/115005265063-Incoming-webhooks-for-Slack).

```yaml
actions:
  visualize: # On demand
    alert:
    - name: slack_alerting
      type: slack
      webhook: <your secret slack URL>

```

### More coming!

Let us know your feature requests in our [Github issues](https://github.com/raymon-ai/raymon/issues)!

