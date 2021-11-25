# Issues

Raymon uses [reducer actions](../actions/reducers.md) to perform periodical checks on your production data. These checks may result in issues, that are then shown on the issues page and may result be raised as alerts.&#x20;

There are several types of issues, as discussed below.

## Issue types and priorities

### Data & model related issues

[Profile reducers](../actions/reducers.md#profile-reducers) are used to perform checks on data quality and model performance. They generate issues that have have different types, locations and impact. Raymon uses these variables to prioritise issues.

#### Issue types

There are several issue types. Ranked in order of priority, they are:

1. Score regression issues
2. Data integrity issues
3. Data cardinality issues
4. Global drift issues
5. Component drift issues

#### Issue locations

Issues may be detected at several "locations". In order of priority:

1. Model evaluations
2. Model actuals
3. Model outputs
4. Model input

#### Issue severity

All issues have a severity metric that is expressed as a % deviation from a baseline. For example, all score regressions and drift metrics are expressed as percentages. This makes it easy for them to be tuned, and allows them to be ordered by their severity.



Raymon orders issues first by issue type, then by issue location and then by issue impact, and only raises alerts for the issue with the highest priority in a slice. All other issues are then presented as debug information for the high-priority issue. For example, this means that a score regression issue on an evaluation metric (e.g. model mean absolute error) has higher priority than an input component drift issue. This input component drift issue may be the cause of the score regression though, which is why it is offered as information for the score regression issue.&#x20;

### Traffic based issues

Coming soon.

## The Issues View

Issues are shown on the issues view on the web UI. On this page, they can be filtered and expanded. See the [walkthrough](../walkthrough-vision/issues-and-tuning.md#filtering-issues) for more info.

