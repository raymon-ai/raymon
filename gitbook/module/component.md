# Component

 _class_ `raymon.InputComponent`\(_name_, _extractor_, _dtype='FLOAT'_, _stats=None_\)[¶](component.md#raymon.InputComponent) `__init__`\(_name_, _extractor_, _dtype='FLOAT'_, _stats=None_\)[¶](component.md#raymon.InputComponent.__init__)

Initialize self. See help\(type\(self\)\) for accurate signature. `build_stats`\(_data_, _domain=None_\)[¶](component.md#raymon.InputComponent.build_stats) `validate`\(_data_\)[¶](component.md#raymon.InputComponent.validate) _classmethod_ `from_jcr`\(_jcr_, _mock\_extractor=False_\)[¶](component.md#raymon.InputComponent.from_jcr)

Given the JSON compatible representation from the function above, load an object of this type with the desired state.Parameters

**jcr** \(_\[dict\]_\) – The jcr representation returned from the to\_jcr function above. Will generally be a dict, but can be anything JSON serializable.Returns

**obj**Return type

type\(this\) _class_ `raymon.OutputComponent`\(_name_, _extractor_, _dtype='FLOAT'_, _stats=None_\)[¶](component.md#raymon.OutputComponent) `__init__`\(_name_, _extractor_, _dtype='FLOAT'_, _stats=None_\)[¶](component.md#raymon.OutputComponent.__init__)

Initialize self. See help\(type\(self\)\) for accurate signature. `build_stats`\(_data_, _domain=None_\)[¶](component.md#raymon.OutputComponent.build_stats) `validate`\(_data_\)[¶](component.md#raymon.OutputComponent.validate) _classmethod_ `from_jcr`\(_jcr_, _mock\_extractor=False_\)[¶](component.md#raymon.OutputComponent.from_jcr)

Given the JSON compatible representation from the function above, load an object of this type with the desired state.Parameters

**jcr** \(_\[dict\]_\) – The jcr representation returned from the to\_jcr function above. Will generally be a dict, but can be anything JSON serializable.Returns

**obj**Return type

type\(this\) _class_ `raymon.ActualComponent`\(_name_, _extractor_, _dtype='FLOAT'_, _stats=None_\)[¶](component.md#raymon.ActualComponent) `__init__`\(_name_, _extractor_, _dtype='FLOAT'_, _stats=None_\)[¶](component.md#raymon.ActualComponent.__init__)

Initialize self. See help\(type\(self\)\) for accurate signature. `build_stats`\(_data_, _domain=None_\)[¶](component.md#raymon.ActualComponent.build_stats) `validate`\(_data_\)[¶](component.md#raymon.ActualComponent.validate) _classmethod_ `from_jcr`\(_jcr_, _mock\_extractor=False_\)[¶](component.md#raymon.ActualComponent.from_jcr)

Given the JSON compatible representation from the function above, load an object of this type with the desired state.Parameters

**jcr** \(_\[dict\]_\) – The jcr representation returned from the to\_jcr function above. Will generally be a dict, but can be anything JSON serializable.Returns

**obj**Return type

type\(this\) _class_ `raymon.EvalComponent`\(_name_, _extractor_, _dtype='FLOAT'_, _stats=None_\)[¶](component.md#raymon.EvalComponent) `__init__`\(_name_, _extractor_, _dtype='FLOAT'_, _stats=None_\)[¶](component.md#raymon.EvalComponent.__init__)

Initialize self. See help\(type\(self\)\) for accurate signature. `build_stats`\(_data_, _domain=None_\)[¶](component.md#raymon.EvalComponent.build_stats) `validate`\(_data_\)[¶](component.md#raymon.EvalComponent.validate) _classmethod_ `from_jcr`\(_jcr_, _mock\_extractor=False_\)[¶](component.md#raymon.EvalComponent.from_jcr)

Given the JSON compatible representation from the function above, load an object of this type with the desired state.Parameters

**jcr** \(_\[dict\]_\) – The jcr representation returned from the to\_jcr function above. Will generally be a dict, but can be anything JSON serializable.Returns

**obj**Return type

type\(this\)

