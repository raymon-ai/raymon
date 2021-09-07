from sklearn.ensemble import IsolationForest

from raymon.profiling.components import ActualComponent, DataType, EvalComponent
import pandas as pd
import sklearn
import numpy as np

from sklearn.model_selection import cross_val_score
from sklearn.datasets import load_iris
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import train_test_split
from raymon.tags import normalize

from raymon import ModelProfile, InputComponent, OutputComponent, ActualComponent
from raymon.profiling.extractors.structured import (
    MaxScoreElementExtractor,
    IsolationForestOutlierScorer,
    ClassificationEntropyExtractor,
    ClassificationMarginExtractor,
    ElementExtractor,
)
from raymon.profiling.extractors.structured import KMeansOutlierScorer
from raymon.profiling.extractors import SequenceSimpleExtractor
from raymon.profiling.extractors.structured.scoring import ClassificationErrorType
from raymon.profiling.scores import MeanScore, PrecisionScore, RecallScore
from raymon.profiling.extractors import SequenceEvalExtractor
from sklearn import preprocessing
from raymon.profiling.extractors.vision import YoloConfidenceExtractor, Sharpness

#%%


def test_profile_multiple():
    """
    Tests a profile and a bunch of extractors pretty lazily, untill we can structure these tests better.
    """
    bunch = load_iris(return_X_y=False, as_frame=False)
    feature_names = [normalize(s) for s in bunch.feature_names]
    target_names = bunch.target_names
    X = bunch.data
    y = target_names[bunch.target]

    clf = AdaBoostClassifier(n_estimators=100)
    clf.fit(X=X, y=y)
    preds = clf.predict_proba(X)

    # track input components (4)
    input_components = []
    for i, name in enumerate(feature_names):
        input_components.append(InputComponent(name=name, extractor=ElementExtractor(element=i), dtype=DataType.FLOAT))

    # track error types (3)
    class_errors = []
    for output_class in target_names:
        eval_component = EvalComponent(
            name=f"{output_class}_errortype",
            extractor=SequenceEvalExtractor(
                prep_output=[MaxScoreElementExtractor(categories=target_names)],
                prep_actual=[],
                eval_extractor=ClassificationErrorType(positive=output_class),
            ),
            dtype=DataType.CAT,
        )
        class_errors.append(eval_component)

    # calculate precision and recall scores
    class_scores = []
    for output_class in target_names:
        class_scores.extend(
            [
                PrecisionScore(name=f"{output_class}_precision", inputs=[f"{output_class}_errortype"]),
                RecallScore(name=f"{output_class}_recall", inputs=[f"{output_class}_errortype"]),
            ]
        )
    iforest = IsolationForest(n_estimators=100)
    iforest.fit(X)
    profile = ModelProfile(
        name="Iris",
        version="1.0.0",
        components=input_components  # 4
        + class_errors  # 3
        + [
            InputComponent(
                name="outlier_score",
                dtype=DataType.FLOAT,
                extractor=IsolationForestOutlierScorer(iforest=iforest),
            ),
            OutputComponent(name="class_margin", extractor=ClassificationMarginExtractor()),
            OutputComponent(name="entropy", extractor=ClassificationEntropyExtractor()),
            OutputComponent(
                name="prediction", extractor=MaxScoreElementExtractor(categories=target_names), dtype=DataType.CAT
            ),
            ActualComponent(name="actual", extractor=ElementExtractor(0), dtype=DataType.CAT),
        ],
        scores=class_scores + [MeanScore(name="mean_margin", inputs=["class_margin"], preference="high")],
    )

    profile.build(input=X, output=preds, actual=y[:, None])
    poi = profile.validate_all(input=X[0, :], output=preds[0, :], actual=y[0, None])
    assert len(poi) >= 11

    ModelProfile.from_jcr(profile.to_jcr())


def test_profile_coco(cocodata):
    images, outputs = cocodata

    profile = ModelProfile(
        name="Yolo",
        version="1.0.0",
        components=[
            InputComponent(name="sharpness", dtype=DataType.FLOAT, extractor=Sharpness()),
            OutputComponent(name="confidence", extractor=YoloConfidenceExtractor()),
        ],
        scores=[MeanScore(name="mean_confidence", inputs=["confidence"], preference="high")],
    )

    profile.build(input=images, output=outputs, silent=False)
    # %%
    poi_inputs = profile.validate_input(input=images[0])
    poi_outputs = profile.validate_output(output=outputs[0])
    poi = poi_inputs + poi_outputs
    assert len(poi) == 2
