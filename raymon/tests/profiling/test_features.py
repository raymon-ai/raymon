#%%
from raymon.profiling.components import DataType
import pytest

import pandas as pd
import numpy as np

from raymon.profiling.extractors.structured import generate_components
from raymon import InputComponent
from raymon import IntStats, FloatStats, CategoricStats
from raymon import ModelProfile
from raymon.globals import ProfileStateException, DataException
from raymon.profiling.extractors.structured import ElementExtractor

#%%
def test_constuct_comps():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
        "cat2": ["c"] * 5 + ["d"] * 5,
        "num2": [0.2] * 10,
    }
    df = pd.DataFrame(data=cols)
    components = generate_components(dtypes=df.dtypes, complass=InputComponent)
    assert len(components) == 4
    assert all(isinstance(c, InputComponent) for c in components)
    assert isinstance(components[0].stats, IntStats)
    assert isinstance(components[1].stats, CategoricStats)
    assert isinstance(components[2].stats, CategoricStats)
    assert isinstance(components[3].stats, FloatStats)


def test_compile():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
    }
    df = pd.DataFrame(data=cols)
    components = generate_components(dtypes=df.dtypes, complass=InputComponent)
    schema = ModelProfile(components=components)
    assert not schema.is_built()
    schema.build(input=df)
    components = schema.components
    assert isinstance(components["num1"].stats, IntStats)
    assert components["num1"].stats.min == 0
    assert components["num1"].stats.max == 9
    assert components["num1"].stats.mean == 4.5
    assert components["num1"].is_built()

    assert isinstance(components["cat1"].stats, CategoricStats)
    assert sorted(components["cat1"].stats.frequencies.keys()) == sorted(["a", "b"])
    assert components["cat1"].stats.invalids == 0
    assert components["cat1"].is_built()

    assert schema.is_built()


def test_compile_one():
    arr = np.array([1, 2, 3, 4, 5])[:, None]
    schema = ModelProfile(
        components=[InputComponent(name="predicted_price", extractor=ElementExtractor(element=0), dtype=DataType.INT)],
    )
    assert not schema.is_built()
    schema.build(input=arr)
    components = schema.components
    assert isinstance(components["predicted_price"].stats, IntStats)
    assert components["predicted_price"].stats.min == 1
    assert components["predicted_price"].stats.max == 5
    assert components["predicted_price"].is_built()

    assert schema.is_built()


def test_all_nan():
    cols = {
        "num1": [np.nan] * 10,
        "cat1": [np.nan] * 10,
    }
    df = pd.DataFrame(data=cols)
    components = generate_components(dtypes=df.dtypes)
    schema = ModelProfile(components=components)
    try:
        schema.build(input=df)
    except ValueError:
        pass
    else:
        pytest.fail("Component with all nans should throw a DataException")


# %%
