# Slices

## Slices[¶](slices.md#slices)

Next to tags, slices are another fundamental concept of Raymon. A slice is simply a subset of a dataset. Slicing your \(production\) data provides valuable, more granular, insights than only looking at the dataset as one whole. A slice is defined by a so called slice string \(`slicestr`\), which is a combination of filters. Any trace matching all filters in the `slicestr` will be in the slice defined by that `slicestr`.

A `slicestr` looks as follows:

```text
client==bigshot && model_version>=1.0.0
```

The `slicestr` above efines all data coming from client “bigshot”, that has been tagged as processed by a model with version &gt;= 1.0.0.

### Slicing options[¶](slices.md#slicing-options)

As already stated, a `slicestr` consists out of a combination of multiple tag filters. Raymon currently supports the following tag filter options.

| Tag filter options |  |  |
| :--- | :--- | :--- |
|  |  |  |
| Tag filter | Description | Example |
| `trace()` | Matches all traces with a given `trace_id`. This should only match 1 trace. | `trace()` |
| `tagname()` | Matches all traces that have a tag with the given name, whatever the value for that tag may be. | `tagname(client)` |
| `tagtype()` | Matches all traces that have a tag with the given type, whatever the name and value for that tag may be. | `tagtype(error)`, `tagtype(profile-actual)` |
| `taggroup()` | Matches all traces that have a tag with the given group, whatever the name, value or type for that tag may be. | `taggroup(client)` |
| `==)` | Matches all traces that have a tag with the given name and a value of that tag equal to the given value. | `client==bigshot` |
| `!=` | Matches all traces that have a tag with the given name and a value of that tag not equal to the given value. | `client!=bigshot` |
| `>=` | Matches all traces that have a tag with the given name and a value of that tag greater than or equal to the given value. | `outlier_score>=50`, `abs_error>=10` |
| `<=` | Matches all traces that have a tag with the given name and a value of that tag smaller than or equal to the given value. | `outlier_score<=50`, `abs_error<=10` |

### Using slices[¶](slices.md#using-slices)

Slice strings have multiple uses in Raymon. A few examples what slices allow you to do:

* Fetch data in a slice \(api\)
* Filter data for the dashboard or trace views \(web UI\)
* Compare 2 slices on the dashboard view \(web UI\)
* Detect issues \(like model accuracy issues\) per slice \(backend / web UI\)

This is further explained in [UI Overview](ui-overview.md#ui-overview).

