# ModelProfile

Your component extractor must be Buildable. This means that it may use data to set some reference values, used to calculate the component to be extracted from a data sample. A good example for this is the raymon.profiling.extractors.structured.KMeansOutlierScorer extractor, which clusters the data at building time and saves those clusters as reference in the objects state. If you dont require and buildabe state, like the raymon.profiling.extractors.structured.ElementExtractor, don’t do anything in this function.Parameters

**data** \(_any_\) – The set of data available at building time. Can be any type you want.ReturnsReturn type

None

