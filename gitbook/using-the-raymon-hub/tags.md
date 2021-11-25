# Tags



Tags are a core concept of Raymon, both for the raymon library and on the Raymon platform. A tag has a `name`, `value`, `type` and optionally a `group `. Tags can be used to attach any type of metadata to a [trace](untitled.md). These tags can then be used to [slice](slices.md) your production data for monitoring or analysis.

Adding tags to a trace is very easy:

```python
tags = [{
    "name": "choose_one",
    "value": "numeric or text",
    "type": "label",
    "group": None
}]

trace.tag(tags)
```

A little extra information about the tag fields may be in order, so here we go:

| Field   | Notes                                                                                                                                                                                                                                                                                                                                                                                     |   |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | - |
| `name`  | A name you choose for the tag. Must adhere to the regex `^[a-zA-Z0-9]+[a-zA-Z0-9_-@.]*$ `For example: `client`, `machine_id`, `IoU@50` are valid tag names.                                                                                                                                                                                                                               |   |
| `value` | A value. Numeric or textual. For example: `0.5`, `9000`, `cat`                                                                                                                                                                                                                                                                                                                            |   |
| `type`  | A string. Some types are [predefined](../../raymon/tags.py) and should be used carefully, but you can choose any other type you want. Most of your custom tags should be of type `label`, `metric` or `error` Types allow the UI to give your tag a fancy color and allow the backend to interpret tags. Tags coming from ModelProfiles will have specific [types](../../raymon/tags.py). |   |
| `group` | A string. Allows you and the backend to group types. For example, all tags coming fro a ModelProfile will have a group identifying that profile, for example `housepricescheap@3.0.0`                                                                                                                                                                                                     |   |

Tags coming from validating data using a model profile look as follows:

```javascript
[{'type': 'profile-input',
  'name': 'mssubclass',
  'value': 70,
  'group': 'housepricescheap@3.0.0'},
 {'type': 'profile-input',
  'name': 'lotarea',
  'value': 9550,
  'group': 'housepricescheap@3.0.0'},
 {'type': 'profile-input',
  'name': 'overallqual',
  'value': 7,
  'group': 'housepricescheap@3.0.0'},
 {'type': 'profile-input',
  'name': 'overallcond',
  'value': 5,
  'group': 'housepricescheap@3.0.0'},
 {'type': 'profile-input',
  'name': 'yearbuilt',
  'value': 1915,
  'group': 'housepricescheap@3.0.0'},
 {'type': 'profile-input',
  'name': 'yearremodadd',
  'value': 1970,
  'group': 'housepricescheap@3.0.0'},
  ...
  ]
```

Raymon uses tags heavily. Monitoring, slicing, data filtering, and more is done based on those tags.&#x20;

