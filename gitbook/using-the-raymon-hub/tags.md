# Tags



Tags are a core concept of raymon, both for the raymon library and on the Raymon platform. A tag is a dictionary that has a `name`, `value`, `type` and optionally a `group `key. Tags can be used to attach any type of metadata to a [trace](untitled.md).&#x20;

Tags may look las follows:

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

Raymon uses tags heavily. Basically everything: monitoring, slicing, data filtering, and more is done based on those tags.&#x20;

