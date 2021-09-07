# Data Types

 _class_ `raymon.types.RaymonDataType`[¶](data-types.md#raymon.types.RaymonDataType) `to_json`\(\)[¶](data-types.md#raymon.types.RaymonDataType.to_json) `to_msgpack`\(\)[¶](data-types.md#raymon.types.RaymonDataType.to_msgpack) `class2str`\(\)[¶](data-types.md#raymon.types.RaymonDataType.class2str) _class_ `raymon.types.Image`\(_data_, _lossless=False_\)[¶](data-types.md#raymon.types.Image) `__init__`\(_data_, _lossless=False_\)[¶](data-types.md#raymon.types.Image.__init__)

Initialize self. See help\(type\(self\)\) for accurate signature. `validate`\(_data_, _lossless_\)[¶](data-types.md#raymon.types.Image.validate) `to_jcr`\(\)[¶](data-types.md#raymon.types.Image.to_jcr)

Return a JSON compatible representation of the object. Will generally return a dict cintaining the objects state, but can return anything JSON serializable. json.dumps\(xxx\) will be called on the output xxx of this function. _classmethod_ `from_jcr`\(_params_\)[¶](data-types.md#raymon.types.Image.from_jcr)

Given the JSON compatible representation from the function above, load an object of this type with the desired state.Parameters

**jcr** \(_\[dict\]_\) – The jcr representation returned from the to\_jcr function above. Will generally be a dict, but can be anything JSON serializable.Returns

**obj**Return type

type\(this\) _class_ `raymon.types.Numpy`\(_data_\)[¶](data-types.md#raymon.types.Numpy) `__init__`\(_data_\)[¶](data-types.md#raymon.types.Numpy.__init__)

Initialize self. See help\(type\(self\)\) for accurate signature. `validate`\(_data_\)[¶](data-types.md#raymon.types.Numpy.validate) `to_jcr`\(\)[¶](data-types.md#raymon.types.Numpy.to_jcr)

Return a JSON compatible representation of the object. Will generally return a dict cintaining the objects state, but can return anything JSON serializable. json.dumps\(xxx\) will be called on the output xxx of this function. _classmethod_ `from_jcr`\(_params_\)[¶](data-types.md#raymon.types.Numpy.from_jcr)

Given the JSON compatible representation from the function above, load an object of this type with the desired state.Parameters

**jcr** \(_\[dict\]_\) – The jcr representation returned from the to\_jcr function above. Will generally be a dict, but can be anything JSON serializable.Returns

**obj**Return type

type\(this\) _class_ `raymon.types.Series`\(_data_\)[¶](data-types.md#raymon.types.Series) `__init__`\(_data_\)[¶](data-types.md#raymon.types.Series.__init__)

Initialize self. See help\(type\(self\)\) for accurate signature. `validate`\(_data_\)[¶](data-types.md#raymon.types.Series.validate) `to_jcr`\(\)[¶](data-types.md#raymon.types.Series.to_jcr)

Return a JSON compatible representation of the object. Will generally return a dict cintaining the objects state, but can return anything JSON serializable. json.dumps\(xxx\) will be called on the output xxx of this function. _classmethod_ `from_jcr`\(_jcr_\)[¶](data-types.md#raymon.types.Series.from_jcr)

Given the JSON compatible representation from the function above, load an object of this type with the desired state.Parameters

**jcr** \(_\[dict\]_\) – The jcr representation returned from the to\_jcr function above. Will generally be a dict, but can be anything JSON serializable.Returns

**obj**Return type

type\(this\) _class_ `raymon.types.DataFrame`\(_data_\)[¶](data-types.md#raymon.types.DataFrame) `__init__`\(_data_\)[¶](data-types.md#raymon.types.DataFrame.__init__)

Initialize self. See help\(type\(self\)\) for accurate signature. `validate`\(_data_\)[¶](data-types.md#raymon.types.DataFrame.validate) `to_jcr`\(\)[¶](data-types.md#raymon.types.DataFrame.to_jcr)

Return a JSON compatible representation of the object. Will generally return a dict cintaining the objects state, but can return anything JSON serializable. json.dumps\(xxx\) will be called on the output xxx of this function. _classmethod_ `from_jcr`\(_jcr_\)[¶](data-types.md#raymon.types.DataFrame.from_jcr)

Given the JSON compatible representation from the function above, load an object of this type with the desired state.Parameters

**jcr** \(_\[dict\]_\) – The jcr representation returned from the to\_jcr function above. Will generally be a dict, but can be anything JSON serializable.Returns

**obj**Return type

type\(this\) _class_ `raymon.types.Native`\(_data_\)[¶](data-types.md#raymon.types.Native) `__init__`\(_data_\)[¶](data-types.md#raymon.types.Native.__init__)

Initialize self. See help\(type\(self\)\) for accurate signature. `validate`\(_data_\)[¶](data-types.md#raymon.types.Native.validate) `to_jcr`\(\)[¶](data-types.md#raymon.types.Native.to_jcr)

Return a JSON compatible representation of the object. Will generally return a dict cintaining the objects state, but can return anything JSON serializable. json.dumps\(xxx\) will be called on the output xxx of this function. _classmethod_ `from_jcr`\(_jcr_\)[¶](data-types.md#raymon.types.Native.from_jcr)

Given the JSON compatible representation from the function above, load an object of this type with the desired state.Parameters

**jcr** \(_\[dict\]_\) – The jcr representation returned from the to\_jcr function above. Will generally be a dict, but can be anything JSON serializable.Returns

**obj**Return type

type\(this\) `raymon.types.load_jcr`\(_jcr_\)[¶](data-types.md#raymon.types.load_jcr) `raymon.types.from_msgpack`\(_data_\)[¶](data-types.md#raymon.types.from_msgpack)

