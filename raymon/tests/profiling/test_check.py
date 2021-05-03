import pandas as pd
import numpy as np

from raymon.profiling.extractors.structured import generate_components
from raymon import ModelProfile


def test_compile_nan():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
    }
    df = pd.DataFrame(data=cols)
    components = generate_components(dtypes=df.dtypes)
    schema = ModelProfile(input_components=components)
    schema.build(input=df)

    tags = schema.validate_input(input=pd.Series([np.nan, np.nan], index=["num1", "cat1"]))
    assert len(tags) == 2
    for tag in tags:
        assert tag["type"] == "profile-input-error"
        assert tag["value"] == "Value NaN"


def test_compile_nan_2():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
    }
    df = pd.DataFrame(data=cols)
    components = generate_components(dtypes=df.dtypes)
    schema = ModelProfile(input_components=components)
    schema.build(input=df)
    components = schema.input_components

    tags = schema.validate_input(input=pd.Series([1, "b"], index=["num1", "cat1"]))
    assert len(tags) == 2

    assert tags[0]["type"] == "profile-input"
    assert tags[0]["name"] == "num1"
    assert tags[0]["value"] == 1
    assert tags[0]["group"] == "default@0.0.0"

    assert tags[1]["type"] == "profile-input"
    assert tags[1]["name"] == "cat1"
    assert tags[1]["value"] == "b"
    assert tags[1]["group"] == "default@0.0.0"
