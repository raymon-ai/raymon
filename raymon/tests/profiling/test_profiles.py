#%%
from raymon.tests.conftest import cheap_houses_csv
import pytest
import json
import pandas as pd
from raymon import InputComponent, OutputComponent, ActualComponent, EvalComponent
from raymon import ModelProfile
from raymon.profiling.extractors.structured import generate_components, ElementExtractor
from raymon.profiling.extractors.structured.scoring import AbsoluteRegressionError
from raymon.profiling import MeanScore


def test_schema_contrast_alternatives(cheap_houses_csv):
    cheap_data = pd.read_csv(cheap_houses_csv).drop("Id", axis="columns")
    actuals = cheap_data["SalePrice"].to_numpy()
    preds = actuals - actuals * 0.1
    keys = ["LotArea", "LotShape", "1stFlrSF", "GrLivArea", "BldgType"]
    inputs = cheap_data[keys]

    def get_profile():
        profile = ModelProfile(
            name="cheap-houses",
            version="0.0.1",
            components=generate_components(inputs.dtypes, complass=InputComponent)
            + [
                OutputComponent(name="prediction", extractor=ElementExtractor(element=0)),
                ActualComponent(name="actual", extractor=ElementExtractor(element=0)),
                EvalComponent(name="abs_error", extractor=AbsoluteRegressionError()),
            ],
            scores=[
                MeanScore(
                    name="MAE",
                    inputs=["abs_error"],
                    preference="low",
                    result=None,
                )
            ],
        )
        profile.build(input=inputs, output=preds[:, None], actual=actuals[:, None])
        return profile

    profile_a = get_profile()
    profile_b = get_profile()
    profile_c = get_profile()

    contrast = profile_a.contrast_alternatives(alternativeA=profile_b, alternativeB=profile_c)
    assert len(contrast["health_reports"]) == len(profile_a.components)
    assert len(contrast["score_reports"]) == 1


def test_schema_contrast_missingcomponents(cheap_houses_csv):
    cheap_data = pd.read_csv(cheap_houses_csv).drop("Id", axis="columns")
    actuals = cheap_data["SalePrice"].to_numpy()
    preds = actuals - actuals * 0.1
    keys = ["LotArea", "LotShape", "1stFlrSF", "GrLivArea", "BldgType"]
    inputs = cheap_data[keys]
    profile = ModelProfile(
        name="cheap-houses",
        version="0.0.1",
        components=generate_components(inputs.dtypes, complass=InputComponent)
        + [
            OutputComponent(name="prediction", extractor=ElementExtractor(element=0)),
            ActualComponent(name="actual", extractor=ElementExtractor(element=0)),
            EvalComponent(name="abs_error", extractor=AbsoluteRegressionError()),
        ],
        scores=[
            MeanScore(
                name="MAE",
                inputs=["abs_error"],
                preference="low",
                result=None,
            )
        ],
    )

    profile.build(input=inputs, output=preds[:, None], actual=actuals[:, None])

    profile_dropped = ModelProfile(
        name="cheap-houses-dropped",
        version="0.0.1",
        components=generate_components(inputs.dtypes, complass=InputComponent)
        + [
            OutputComponent(name="prediction", extractor=ElementExtractor(element=0)),
        ],
    )
    profile_dropped.build(input=inputs, output=preds[:, None])

    contrast = profile.contrast(profile_dropped)
    assert all(k.lower() in contrast["health_reports"] for k in keys)
    assert "actual" not in contrast["health_reports"]
    assert len(contrast["score_reports"]) == 0


def test_schema_contrast_missingcomponents(cheap_houses_csv):
    cheap_data = pd.read_csv(cheap_houses_csv).drop("Id", axis="columns")
    actuals = cheap_data["SalePrice"].to_numpy()
    preds = actuals - actuals * 0.1
    keys = ["LotArea", "LotShape", "1stFlrSF", "GrLivArea", "BldgType"]
    inputs = cheap_data[keys]
    profile = ModelProfile(
        name="cheap-houses",
        version="0.0.1",
        components=generate_components(inputs.dtypes, complass=InputComponent)
        + [
            OutputComponent(name="prediction", extractor=ElementExtractor(element=0)),
            ActualComponent(name="actual", extractor=ElementExtractor(element=0)),
            EvalComponent(name="abs_error", extractor=AbsoluteRegressionError()),
        ],
        scores=[
            MeanScore(
                name="MAE",
                inputs=["abs_error"],
                preference="low",
                result=None,
            )
        ],
    )

    profile.build(input=inputs, output=preds[:, None], actual=actuals[:, None])

    profile_dropped = ModelProfile(
        name="cheap-houses-dropped",
        version="0.0.1",
        components=generate_components(inputs.dtypes, complass=InputComponent)
        + [
            OutputComponent(name="prediction", extractor=ElementExtractor(element=0)),
            ActualComponent(name="actual", extractor=ElementExtractor(element=0)),
            EvalComponent(name="abs_error", extractor=AbsoluteRegressionError()),
        ],
        scores=[
            MeanScore(
                name="MAE",
                inputs=["abs_error"],
                preference="low",
                result=None,
            )
        ],
    )
    profile_dropped.build(input=inputs, output=preds[:, None], actual=actuals[:, None])

    contrast = profile.contrast(profile_dropped)
    assert all(k.lower() in contrast["health_reports"] for k in keys)
    assert len(contrast["score_reports"]) == 1


def test_schema_build_input_types(cheap_houses_csv):
    cheap_data = pd.read_csv(cheap_houses_csv).drop("Id", axis="columns")
    actuals = cheap_data["SalePrice"]
    preds = actuals - actuals * 0.1
    keys = ["LotArea", "LotShape", "1stFlrSF", "GrLivArea", "BldgType"]
    inputs = cheap_data[keys]
    profile = ModelProfile(
        name="cheap-houses",
        version="0.0.1",
        components=generate_components(inputs.dtypes, complass=InputComponent)
        + [
            OutputComponent(name="prediction", extractor=ElementExtractor(element=0)),
            ActualComponent(name="actual", extractor=ElementExtractor(element=0)),
            EvalComponent(name="abs_error", extractor=AbsoluteRegressionError()),
        ],
    )
    # Try pandas Series, the [;, None] indexing is actually deprecated
    profile.build(input=inputs, output=preds.to_frame(name=0), actual=actuals.to_frame(name=0))
    assert profile.components["prediction"].stats.samplesize == 992
    assert profile.components["actual"].stats.samplesize == 992
    assert profile.components["abs_error"].stats.samplesize == 992

    # Try numpy arrays
    actuals_np = actuals.to_numpy()
    preds_np = preds.to_numpy()
    profile.build(input=inputs, output=preds_np[:, None], actual=actuals_np[:, None])
    assert profile.components["prediction"].stats.samplesize == 992
    assert profile.components["actual"].stats.samplesize == 992
    assert profile.components["abs_error"].stats.samplesize == 992
    # Try lsits
    actuals_list = actuals[:, None].tolist()
    preds_list = preds[:, None].tolist()
    profile.build(input=inputs, output=preds_list, actual=actuals_list, silent=False)
    assert profile.components["prediction"].stats.samplesize == 992
    assert profile.components["actual"].stats.samplesize == 992
    assert profile.components["abs_error"].stats.samplesize == 992
    return profile, actuals_list, preds_list
