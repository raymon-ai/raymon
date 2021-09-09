---
description: >-
  This section describes how you can use model profiles to monitor data quality
  and drift.
---

# Contrasting Profiles

In the previous section we saw how we can use model profiles to validate individual datums. Here, we'll discuss how to use model profiles to guard agains data quality degradations and data drift.

## Monitoring data quality

Let's assume you have 2 datasets that you want to monitor for rift or performance decay. We'll build on the house price prediction example from [earlier](building-house-prices.md). We built it as follows:

```python
profile = ModelProfile(
    name="HousePricesCheap",
    version="3.0.0",
    components=[
        InputComponent(
            name="outlier_score",
            extractor=SequenceSimpleExtractor(prep=coltf, extractor=KMeansOutlierScorer()),
        ),
        OutputComponent(name="prediction", extractor=ElementExtractor(element=0)),
        ActualComponent(name="actual", extractor=ElementExtractor(element=0)),
        EvalComponent(name="abs_error", extractor=AbsoluteRegressionError()),
    ] + generate_components(X_test[feature_selector].dtypes, complass=InputComponent),
    scores=[
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
    ],
)
profile.build(input=X_test[feature_selector], output=y_pred[:, None], actual=y_test[:, None])
profile.view()
```

Now, say we have collected a 

* 2 profiles
* 


## Thresholds & Tuning

* How to set & pass them
* How drift is calculated and why: tunability

