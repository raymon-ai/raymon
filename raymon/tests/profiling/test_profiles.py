#%%
from raymon.tests.conftest import cheap_houses_csv
import pytest
import json
import copy
import pandas as pd
from raymon import InputComponent, OutputComponent, ActualComponent, EvalComponent
from raymon import ModelProfile
from raymon.profiling.extractors.structured import generate_components, ElementExtractor
from raymon.profiling.extractors.structured.scoring import AbsoluteRegressionError
from raymon.profiling import MeanScore
from raymon.tests.profiling.houseprices_utils import prep_df, train, load_data
from raymon.profiling.extractors.structured import KMeansOutlierScorer
from raymon.profiling.extractors import SequenceSimpleExtractor


def test_schema_contrast_alternatives(cheap_houses_csv):
    cheap_data = pd.read_csv(cheap_houses_csv).drop("Id", axis="columns")

    def get_profile():
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


def test_schema_build_big_houseprices(cheap_houses_csv, exp_houses_csv):

    # Load data
    X_train, y_train = load_data(cheap_houses_csv)
    X_test, y_test = load_data(cheap_houses_csv)  # We use the same train / test data for this test

    X_exp_test, y_exp_test = load_data(exp_houses_csv)

    rf, coltf, feature_selector_ohe, feature_selector = train(X_train=X_train, y_train=y_train)

    Xtf_test = pd.DataFrame(
        coltf.transform(X_test[feature_selector]),
        columns=feature_selector_ohe,
    )
    Xtf_exp_test = pd.DataFrame(
        coltf.transform(X_exp_test[feature_selector]),
        columns=feature_selector_ohe,
    )

    y_pred = rf.predict(Xtf_test[feature_selector_ohe])
    y_exp_pred = rf.predict(Xtf_exp_test[feature_selector_ohe])

    # Construct profiles's
    components = generate_components(X_test[feature_selector].dtypes, complass=InputComponent) + [
        InputComponent(
            name="outlier_score",
            extractor=SequenceSimpleExtractor(prep=coltf, extractor=KMeansOutlierScorer()),
        ),
        OutputComponent(name="prediction", extractor=ElementExtractor(element=0)),
        ActualComponent(name="actual", extractor=ElementExtractor(element=0)),
        EvalComponent(name="abs_error", extractor=AbsoluteRegressionError()),
    ]
    scores = [
        MeanScore(
            name="MAE",
            inputs=["abs_error"],
            preference="low",
        ),
        MeanScore(
            name="mean_outlier_score",
            inputs=["outlier_score"],
            preference="low",
        ),
    ]

    profile = ModelProfile(
        name="HousePricesCheap",
        version="3.0.0",
        components=components,
        scores=scores,
    )
    profile.build(input=X_test[feature_selector], output=y_pred[:, None], actual=y_test[:, None])

    profile_exp = copy.deepcopy(profile)
    profile_exp.name = "HousePricesExpensive"
    profile_exp.build(input=X_exp_test[feature_selector], output=y_exp_pred[:, None], actual=y_exp_test[:, None])

    profile.contrast(profile_exp, thresholds={})
