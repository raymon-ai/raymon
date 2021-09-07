# Tag class

 _class_ `raymon.Tag`\(_name_, _value_, _type_, _group=None_\)[¶](tag-class.md#raymon.Tag)

Represents a tag. Tags are used for monitoring and filtering in the backend.Parameters

* **name** \(_str_\) – Name of the tag
* **value** \(_str_ _or_ _Number_\) – Value of the tag. Can be numeric or string.
* **type** \(_str_\) – Type of the tag. Note: some type string have a special meaning like tags assicuiated with data profiles and errors.
* **group** \(_str,_ _optional_\) – y setting the group, you can indicate that this tag belongs to a certai nset of tagt. For example, all tags that belong to a certai ndata profile will have the same group.

 `__init__`\(_name_, _value_, _type_, _group=None_\)[¶](tag-class.md#raymon.Tag.__init__)

Initialize self. See help\(type\(self\)\) for accurate signature. `to_jcr`\(\)[¶](tag-class.md#raymon.Tag.to_jcr)

Return a JSON compatible representation of the object. Will generally return a dict cintaining the objects state, but can return anything JSON serializable. json.dumps\(xxx\) will be called on the output xxx of this function. _classmethod_ `from_jcr`\(_jcr_\)[¶](tag-class.md#raymon.Tag.from_jcr)

Given the JSON compatible representation from the function above, load an object of this type with the desired state.Parameters

**jcr** \(_\[dict\]_\) – The jcr representation returned from the to\_jcr function above. Will generally be a dict, but can be anything JSON serializable.Returns

**obj**Return type

type\(this\)

