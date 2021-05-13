import pandas as pd
import numpy as np
from raymon.profiling.components import FloatComponent

from raymon.profiling.extractors.structured import generate_comps
from raymon import ModelProfile
from raymon.profiling.extractors.structured.scoring import AbsoluteError


def test_compile_nan():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
    }
    df = pd.DataFrame(data=cols)
    components = generate_comps(dtypes=df.dtypes)
    schema = ModelProfile(input_comps=components)
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
    components = generate_comps(dtypes=df.dtypes)
    schema = ModelProfile(input_comps=components)
    schema.build(input=df)
    components = schema.input_comps

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


def test_valdiate_output():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
    }
    df = pd.DataFrame(data=cols)
    components = generate_comps(dtypes=df.dtypes)
    schema = ModelProfile(output_comps=components)
    schema.build(output=df)
    components = schema.output_comps

    tags = schema.validate_output(output=pd.Series([1, "b"], index=["num1", "cat1"]))
    assert len(tags) == 2
    assert tags[0]["type"] == "profile-output"
    assert tags[0]["name"] == "num1"
    assert tags[0]["value"] == 1
    assert tags[0]["group"] == "default@0.0.0"

    assert tags[1]["type"] == "profile-output"
    assert tags[1]["name"] == "cat1"
    assert tags[1]["value"] == "b"
    assert tags[1]["group"] == "default@0.0.0"


def test_validate_actual():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
    }
    df = pd.DataFrame(data=cols)
    components = generate_comps(dtypes=df.dtypes)
    schema = ModelProfile(actual_comps=components)
    schema.build(actual=df)
    components = schema.actual_comps

    tags = schema.validate_actual(actual=pd.Series([1, "b"], index=["num1", "cat1"]))
    assert len(tags) == 2
    assert tags[0]["type"] == "profile-actual"
    assert tags[0]["name"] == "num1"
    assert tags[0]["value"] == 1
    assert tags[0]["group"] == "default@0.0.0"

    assert tags[1]["type"] == "profile-actual"
    assert tags[1]["name"] == "cat1"
    assert tags[1]["value"] == "b"
    assert tags[1]["group"] == "default@0.0.0"


def test_multiple_component_types():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
    }
    df = pd.DataFrame(data=cols)
    components = generate_comps(dtypes=df.dtypes)
    schema = ModelProfile(input_comps=components, output_comps=components, actual_comps=components)
    schema.build(input=df, output=df, actual=df)

    tags = schema.validate_input(input=pd.Series([1, "b"], index=["num1", "cat1"]))
    assert len(tags) == 2

    tags = schema.validate_output(output=pd.Series([1, "b"], index=["num1", "cat1"]))
    assert len(tags) == 2

    tags = schema.validate_actual(actual=pd.Series([1, "b"], index=["num1", "cat1"]))
    assert len(tags) == 2


def test_score():
    outputs = [2, 1, 2, 0, 1]
    actuals = [0, 1, 2, 1, 2]
    components = [FloatComponent(name="model_abs_error", extractor=AbsoluteError())]
    profile = ModelProfile(eval_comps=components)
    profile.build(output=outputs, actual=actuals)
    assert profile.is_built()

    tags = profile.validate_score(output=outputs[0], actual=actuals[0])
    assert len(tags) == 1
    assert tags[0]["type"] == "profile-score"
