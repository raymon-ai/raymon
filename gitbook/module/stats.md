# Stats

## Stats[¶](stats.md#stats)

 _class_ `raymon.FloatStats`\(_min=None_, _max=None_, _mean=None_, _std=None_, _invalids=None_, _percentiles=None_, _samplesize=None_, _\*\*kwargs_\)[¶](stats.md#raymon.FloatStats) `component2tag`\(_name_, _value_, _tagtype_\)[¶](stats.md#raymon.FloatStats.component2tag) `check_invalid`\(_name_, _value_, _tagtype_\)[¶](stats.md#raymon.FloatStats.check_invalid) _classmethod_ `from_jcr`\(_data_\)[¶](stats.md#raymon.FloatStats.from_jcr)

Given the JSON compatible representation from the function above, load an object of this type with the desired state.Parameters

**jcr** \(_\[dict\]_\) – The jcr representation returned from the to\_jcr function above. Will generally be a dict, but can be anything JSON serializable.Returns

**obj**Return type

type\(this\) _class_ `raymon.IntStats`\(_min=None_, _max=None_, _mean=None_, _std=None_, _invalids=None_, _percentiles=None_, _samplesize=None_, _\*\*kwargs_\)[¶](stats.md#raymon.IntStats) `component2tag`\(_name_, _value_, _tagtype_\)[¶](stats.md#raymon.IntStats.component2tag) `check_invalid`\(_name_, _value_, _tagtype_\)[¶](stats.md#raymon.IntStats.check_invalid) _classmethod_ `from_jcr`\(_data_\)[¶](stats.md#raymon.IntStats.from_jcr)

Given the JSON compatible representation from the function above, load an object of this type with the desired state.Parameters

**jcr** \(_\[dict\]_\) – The jcr representation returned from the to\_jcr function above. Will generally be a dict, but can be anything JSON serializable.Returns

**obj**Return type

type\(this\) _class_ `raymon.CategoricStats`\(_frequencies=None_, _invalids=None_, _samplesize=None_, _\*\*kwargs_\)[¶](stats.md#raymon.CategoricStats) `__init__`\(_frequencies=None_, _invalids=None_, _samplesize=None_, _\*\*kwargs_\)[¶](stats.md#raymon.CategoricStats.__init__)

Initialize self. See help\(type\(self\)\) for accurate signature. _property_ `frequencies`[¶](stats.md#raymon.CategoricStats.frequencies) _property_ `frequencies_lb`[¶](stats.md#raymon.CategoricStats.frequencies_lb) _property_ `frequencies_ub`[¶](stats.md#raymon.CategoricStats.frequencies_ub) _property_ `invalids`[¶](stats.md#raymon.CategoricStats.invalids) _property_ `samplesize`[¶](stats.md#raymon.CategoricStats.samplesize) _property_ `range`[¶](stats.md#raymon.CategoricStats.range) `build`\(_data_, _domain=None_\)[¶](stats.md#raymon.CategoricStats.build)

\[summary\]Parameters

* **data** \(_\[type\]_\) – \[description\]
* **domain** \(_\[type\],_ _optional_\) – The domain of the featrue. A list or set, by default None

 `is_built`\(\)[¶](stats.md#raymon.CategoricStats.is_built)

Check whether the object has been built. Typically, this method checks whether the required references for the object is set. If your ComponentExtractor does not use any references, simply return True.Returns

**is\_built**Return type

bool `get_conf_bounds_poisson`\(_frequencies_\)[¶](stats.md#raymon.CategoricStats.get_conf_bounds_poisson)

Estimate the 95% confidence interval for the distributions, using the “Normal Approximation Method” of the Binomial Confidence Interval. References: - [https://stats.stackexchange.com/questions/111355/confidence-interval-and-sample-size-multinomial-probabilities](https://stats.stackexchange.com/questions/111355/confidence-interval-and-sample-size-multinomial-probabilities) - [https://www.dummies.com/education/science/biology/the-confidence-interval-around-an-event-count-or-rate/](https://www.dummies.com/education/science/biology/the-confidence-interval-around-an-event-count-or-rate/) :param frequencies: \[description\] :type frequencies: \[type\] :param nobs: \[description\] :type nobs: \[type\] `report_drift`\(_other_, _threshold_\)[¶](stats.md#raymon.CategoricStats.report_drift) `sample`\(_n_\)[¶](stats.md#raymon.CategoricStats.sample) `sample_counts`\(_domain\_freq_, _keys_, _n=500_\)[¶](stats.md#raymon.CategoricStats.sample_counts) `component2tag`\(_name_, _value_, _tagtype_\)[¶](stats.md#raymon.CategoricStats.component2tag) `check_invalid`\(_name_, _value_, _tagtype_\)[¶](stats.md#raymon.CategoricStats.check_invalid) _classmethod_ `from_jcr`\(_data_\)[¶](stats.md#raymon.CategoricStats.from_jcr)

Given the JSON compatible representation from the function above, load an object of this type with the desired state.Parameters

**jcr** \(_\[dict\]_\) – The jcr representation returned from the to\_jcr function above. Will generally be a dict, but can be anything JSON serializable.Returns

**obj**Return type

type\(this\)

