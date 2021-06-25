from raymon.profiling.components import DataType
import pytest
import json
from raymon import ModelProfile
from raymon import InputComponent
from raymon import IntStats, FloatStats, CategoricStats
from raymon.profiling.extractors.vision.similarity import FixedSubpatchSimilarity
from raymon.profiling.extractors.structured.scoring import ClassificationErrorType
from raymon.profiling.extractors.vision import DN2AnomalyScorer, AvgIntensity, Sharpness
from raymon.profiling.extractors.structured import ElementExtractor
import numpy as np
import pandas as pd


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


def test_profile_with_vision_data(images, tmp_path):
    profile = ModelProfile(
        name="retinopathy",
        version="2.0.0",
        components=[
            InputComponent(
                name="sharpness",
                extractor=Sharpness(),
                dtype=DataType.FLOAT,
            ),
            InputComponent(
                name="intensity",
                extractor=AvgIntensity(),
                dtype=DataType.FLOAT,
            ),
            InputComponent(
                name="outlierscore",
                extractor=DN2AnomalyScorer(k=5),
                dtype=DataType.FLOAT,
            ),
        ],
    )
    # Build profile: profile
    profile.build(input=images)
    # Save profile
    profile.save(str(tmp_path))
    # Load profile: loaded_profile
    loaded_profile = ModelProfile().load(str(tmp_path) + f"/{profile.group_idfr}.json")
    # Create the jcr of the profile
    loaded_profile_jcr = loaded_profile.to_jcr()
    # jcr checks
    assert len(loaded_profile_jcr["components"]) == 3
    jsonstr = json.dumps(loaded_profile_jcr)  # Should not throw an error
    assert len(jsonstr) > 0
    assert (
        loaded_profile_jcr["components"]["intensity"]["state"]["extractor"]["class"]
        == "raymon.profiling.extractors.vision.intensity.AvgIntensity"
    )
    assert (
        loaded_profile_jcr["components"]["sharpness"]["state"]["extractor"]["class"]
        == "raymon.profiling.extractors.vision.sharpness.Sharpness"
    )
    assert loaded_profile_jcr["components"]["outlierscore"]["state"]["extractor"]["state"]["k"] == 5
    # from_jcr checks
    profile_restored = profile.from_jcr(loaded_profile_jcr)
    assert loaded_profile.name == profile_restored.name
    assert loaded_profile.version == profile_restored.version
    assert all([c1 == c2 for (c1, c2) in zip(loaded_profile.components.keys(), profile_restored.components.keys())])


def test_profile_with_structured_data(tmp_path):
    profile = ModelProfile(
        name="vector",
        version="1.0.0",
        components=[InputComponent(name="actual", extractor=ElementExtractor(element="num1"), dtype=DataType.INT)],
    )
    # Sample data: df
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
        "cat2": ["c"] * 5 + ["d"] * 5,
        "num2": [0.2] * 10,
    }
    df = pd.DataFrame(data=cols)
    # Build profile: profile
    profile.build(input=df)
    # Save profile
    profile.save(str(tmp_path))
    # Load profile: loaded_profile
    loaded_profile = ModelProfile().load(str(tmp_path) + f"/{profile.group_idfr}.json")
    # Create the jcr of the profile
    loaded_profile_jcr = loaded_profile.to_jcr()
    # jcr checks
    assert len(loaded_profile_jcr["components"]) == 1
    jsonstr = json.dumps(loaded_profile_jcr)  # Should not throw an error
    assert len(jsonstr) > 0
    assert loaded_profile_jcr["components"]["actual"]["state"]["extractor"]["state"]["element"] == "num1"
    # from_jcr checks
    profile_restored = profile.from_jcr(loaded_profile_jcr)
    assert loaded_profile.name == profile_restored.name
    assert loaded_profile.version == profile_restored.version
    assert all([c1 == c2 for (c1, c2) in zip(loaded_profile.components.keys(), profile_restored.components.keys())])
