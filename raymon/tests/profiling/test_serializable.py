from raymon.profiling.components import DataType
import pytest
import json
from raymon import ModelProfile
from raymon import InputComponent
from raymon import IntStats, FloatStats, CategoricStats
from raymon.profiling.extractors.vision.similarity import FixedSubpatchSimilarity
from raymon.profiling.extractors.structured.scoring import ClassificationErrorType


def test_schema_jcr():
    extractor = FixedSubpatchSimilarity(
        patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, refs=["adf8d224cb8786cc"], nrefs=1
    )
    stats = FloatStats(min=0, max=1, mean=0.5, std=0.02, percentiles=range(101))
    component = InputComponent(name="testcomponent", extractor=extractor, stats=stats, dtype=DataType.FLOAT)
    component2 = InputComponent(name="testcomponent2", extractor=extractor, stats=stats, dtype=DataType.FLOAT)

    schema = ModelProfile(name="Testing", version="1.0.0", components=[component, component2])
    schema_jcr = schema.to_jcr()
    assert len(schema_jcr["components"]) == 2
    jsonstr = json.dumps(schema_jcr)  # Should not throw an error
    assert len(jsonstr) > 0
    schema_restored = ModelProfile.from_jcr(schema_jcr)

    assert schema.name == schema_restored.name
    assert schema.version == schema_restored.version
    assert all([c1 == c2 for (c1, c2) in zip(schema.components.keys(), schema_restored.components.keys())])


def test_score_json():
    extractor = ClassificationErrorType(positive=1)
    jcr = extractor.to_jcr()
    dumped = json.dumps(jcr)
    assert isinstance(dumped, str)
