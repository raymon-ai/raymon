import pytest
import json
from raymon import FloatComponent, IntComponent
from raymon import ModelProfile
from raymon import NumericStats
from raymon.profiling.extractors.vision.similarity import FixedSubpatchSimilarity
from raymon.profiling.extractors.structured.scoring import ClassificationErrorType


def test_schema_jcr():
    extractor = FixedSubpatchSimilarity(
        patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, refs=["adf8d224cb8786cc"], nrefs=1
    )
    stats = NumericStats(min=0, max=1, mean=0.5, std=0.02, percentiles=range(101))
    component = FloatComponent(name="testcomponent", extractor=extractor, stats=stats)
    component2 = FloatComponent(name="testcomponent2", extractor=extractor, stats=stats)

    schema = ModelProfile(name="Testing", version="1.0.0", input_comps=[component, component2])
    schema_jcr = schema.to_jcr()
    assert len(schema_jcr["input_comps"]) == 2
    jsonstr = json.dumps(schema_jcr)  # Should not throw an error
    assert len(jsonstr) > 0
    schema_restored = ModelProfile.from_jcr(schema_jcr)

    assert schema.name == schema_restored.name
    assert schema.version == schema_restored.version
    assert all([c1 == c2 for (c1, c2) in zip(schema.input_comps.keys(), schema_restored.input_comps.keys())])


def test_score_json():
    extractor = ClassificationErrorType(positive=1)
    jcr = extractor.to_jcr()
    assert "lower_better" in jcr
    dumped = json.dumps(jcr)
    assert isinstance(dumped, str)
