from sklearn.ensemble import IsolationForest

from scipy.sparse.sputils import isscalarlike
from raymon.profiling.extractors.structured.margin import ClassificationMarginExtractor
from raymon.profiling.components import ActualComponent, DataType, EvalComponent
from raymon.profiling.extractors.structured.element import ElementExtractor
from raymon.profiling import extractors
import pandas as pd
import sklearn
import numpy as np

from sklearn.model_selection import cross_val_score
from sklearn.datasets import load_iris
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import train_test_split
from raymon.tags import normalize

from raymon import ModelProfile, InputComponent, OutputComponent, ActualComponent
from raymon.profiling.extractors.structured import MaxScoreElementExtractor, IsolationForestOutlierScorer
from raymon.profiling.extractors.structured.scoring import ClassificationErrorType
from raymon.profiling.scores import MeanScore, PrecisionScore, RecallScore
from raymon.profiling.extractors import SequenceEvalExtractor
from sklearn import preprocessing

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
                sequence_output=[MaxScoreElementExtractor(categories=target_names)],
                sequence_actual=[],
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

    profile = ModelProfile(
        name="Iris",
        version="1.0.0",
        components=input_components  # 4
        + class_errors  # 3
        + [
            InputComponent(
                name="outlier_score",
                dtype=DataType.FLOAT,
                extractor=IsolationForestOutlierScorer(iforest=IsolationForest(n_estimators=100)),
            ),
            OutputComponent(name="class_margin", extractor=ClassificationMarginExtractor()),
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
