---
description: Slices allow you to watch & benchmark subsets of data against each other.
---

# Slices

Just like [tags](tags.md), slices too are a fundamental concept of Raymon. A slice is simply a subset of data. A slice, a subset, a segment, a sample... they are all the same thing: a part of all the data you have.

Raymon uses slices for multiple functionalities. For example, Raymon uses slices for monitoring. Using ModelProfiles, it's easy to set up monitoring. Using slices, it's easy to perform this monitoring for subsets of data and get more granular alerts, shortening time to resolution dramatically. For example,  monitoring your data for each client individually will give you targeted alerts like "_client x is sending bad data_" in contradiction to "_a part of all your data is bad data_" without slices. This shortens the time-to-resolution dramatically.&#x20;

Other things you can do with slices include:

* Fetch data in a slice (api)
* Filter data for the dashboard or trace views (web UI)
* Compare 2 slices on the dashboard view (web UI)

### Slice strings

A slice is defined by a so called slice string (`slicestr`), which is a combination of filters. Any trace matching all filters in the `slicestr` will be in the slice defined by that `slicestr`.

A `slicestr` looks as follows:

```
client==bigshot && model_version>=1.0.0
```

The `slicestr` above defines all data tagged as coming from client "_bigshot_", that has been tagged as processed by a model with _model\_version_ >= 1.0.0.

The available tag filters are listed in the table below.&#x20;



| Tag filter              | Description                                                                                                              | Example                                     |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------- |
| `trace(<trace_id>)`     | Matches all traces with a given `trace_id`. This should only match 1 trace.                                              | `trace("thisisanid")`                       |
| `tagname(<tag_name>)`   | Matches all traces that have a tag with the given name, whatever the value for that tag may be.                          | `tagname(client)`                           |
| `tagtype(<tag_type>)`   | Matches all traces that have a tag with the given type, whatever the name and value for that tag may be.                 | `tagtype(error)`, `tagtype(profile-actual)` |
| `taggroup(<tag_group>)` | Matches all traces that have a tag with the given group, whatever the name, value or type for that tag may be.           | `taggroup(client)`                          |
| `<tag>==<value>)`       | Matches all traces that have a tag with the given name and a value of that tag equal to the given value.                 | `client==bigshot`                           |
| `<tag>!=<value>`        | Matches all traces that have a tag with the given name and a value of that tag not equal to the given value.             | `client!=bigshot`                           |
| `<tag>>=<value>`        | Matches all traces that have a tag with the given name and a value of that tag greater than or equal to the given value. | `outlier_score>=50`, `abs_error>=10`        |
| `<tag><=<value>`        | Matches all traces that have a tag with the given name and a value of that tag smaller than or equal to the given value. | `outlier_score<=50`, `abs_error<=10`        |

### Slice search spaces

Manually defining all slices using a `slicestr` may be cumbersome. Imagine having 100 clients on your system that are all tagged with the tag `client==<their_id>`. To monitor all those clients individually using a`slicestr` would require you to specify 100 different slice strings.

For this purpose, Raymon support slice search spaces. A slice search space is a list of tags, and defines all slices that can be made with any combination of those tag's values. For example, consider the space below.

```yaml
 - space:
   - tag: client
   - tag: app
```

This space definition will make Raymon do the following:

* Look up all unique values for the `client` tag (within a given time window)
* Look up all unique values for the `app` tag (within a given time window)
* Make all unique combinations of those (e.g. `client==Remax && app==v1.0.0)`

<mark style="color:red;">Note</mark>: slice spaces grow exponentially! Be careful when using them, as the amount of slices to analyse will impact the processing power Raymon requires (and pricing).

## Setting up slice-based monitoring

To set up slice-based monitoring, all you need to do is add a slices section to the project [manifest](the-manifest.md).&#x20;

```yaml
slices:
  - slicestr: client==Remax && app==v1.0.0
  - space:
      - tag: client
  - space:
      - tag: client
      - tag: app
```

## Other uses

Slice strings can be used on the [dashboards](dashboards.md) for analysis purposes.
