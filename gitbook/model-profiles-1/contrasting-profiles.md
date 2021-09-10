---
description: >-
  This section describes how you can use model profiles to monitor data quality
  and drift.
---

# Contrasting Profiles

In the previous section we saw how we can use model profiles to validate individual datums. Here, we'll discuss how to use model profiles to guard agains data quality degradations and data drift.

## Monitoring data quality

Let's assume you have 2 datasets that you want to monitor for drift or performance decay. One could be your training set, the other could be data collected from production. We'll build on the house price prediction profiel from [earlier](building-house-prices.md). We've built it as follows:

```python
profile = ModelProfile(
    name="HousePricesCheap",
    version="3.0.0",
    components=[
        InputComponent(
            name="outlier_score",
            extractor=SequenceSimpleExtractor(
                prep=coltf, extractor=KMeansOutlierScorer()),
        ),
        OutputComponent(name="prediction", extractor=ElementExtractor(element=0)),
        ActualComponent(name="actual", extractor=ElementExtractor(element=0)),
        EvalComponent(name="abs_error", extractor=AbsoluteRegressionError()),
    ] + generate_components(X_train[feature_selector].dtypes, 
                            complass=InputComponent),
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
profile.build(input=X_val[feature_selector], 
              output=y_pred_val[:, None], 
              actual=y_val[:, None])
```

Now, say we have collected a sample of production data into another CSV file. We will simulate this by loading another CSV file, just as before. 

```python
exp_houses_csv = "../raymon/tests/sample_data/houseprices/subset-exp.csv"
X_exp_test, y_exp_test = load_data(exp_houses_csv)

# Make sure we have model predictions too
Xtf_exp_test = pd.DataFrame(
    coltf.transform(X_exp_test[feature_selector]),
    columns=feature_selector_ohe,
)
y_exp_pred = rf.predict(Xtf_exp_test[feature_selector_ohe])
```

We can use this data to build another profile, based on the current one as follows.

```python
import copy

profile_exp = copy.deepcopy(profile)
profile_exp.name = "HousePricesExp"
profile_exp.version = "3.0.0"
profile_exp.build(input=X_exp_test[feature_selector], 
                  output=y_exp_pred[:, None], 
                  actual=y_exp_test[:, None], build_extractors=False)
profile_exp.view()
```

Notice that we pass the `build_extractors=False` flag. This makes sure we do not rebuild the extractors. One of the extractors is a novelty detector, which needs to be trained on the original data used at model training. We do not want to retrain this outlier detector on production data.

When viewing the profile, it should look similar as before. But, now that we have 2 profiles, we can contrast them against each other!

```python
profile.view_contrast(profile_exp)
```

This gives us a the following view, where the original profile is displayed in grey, and the new one in blue. This allows us to spot differences easily. We'll go over different areas of interest below the image.

![Contrasting 2 profiles agains each other.](../.gitbook/assets/image%20%2814%29.png)

### Data integrity

For every component, the next to last columns shows the amount of invalid values encountered in the data when building the profile. Remember, invalid values can be Nones, NaN or out-of-domain values. The invalids columns shows the percentage invalids in the original profile, the percentage in the new profile and the change in percentage points. By clicking the arrows you can easily sort by percentage point change.

### Drift

The drift columns shows how much the data distributions have changed. In the image above, the column has been sorted from high to low. The distance is always between 0% and 100% and is the distance between the 90% confidence intervals of the distributions. For categorical data, the Chebyshev distance is used. For numerical data, we use the same distance metric as in the Kolmogorov-Smirnov test: the maximum distance between the CDF distributions. 

### Scores

Lastly, we also see the difference between the model scores at the top. Here, we see that the mean average error the model made has increased dramatically between the 2 profiles. The outlier score is also much higher on average. 

![](../.gitbook/assets/image%20%2813%29.png)

Going from the many warning signals we have, we can conclude something is wrong with our data. We don't get a lot on invalid values, but something in the distribution has certainly changed, and our model is not performing well because of it. 

After inspecting the output and actual tabs of the component views, it should be clear what is wrong here. What happened is that, apparently, our system has been processing houses in a higher price range than what we have seen during training, and our model is struggling with that. Time to retrain your model with new and more relevant data!

![The actuals we are trying to predict have shifted dramatically.](../.gitbook/assets/image%20%2811%29.png)

## Warning reports

Instead of visualising the drift report, you may only be interested in getting warnings. You can get a report by calling `profile.contrast()`

```python
report = profile.contrast(profile_exp)
```

This will output a dictionary with the following keys.

| Key | Description |
| :--- | :--- |
| `reference` | Contains the JSON Compatible Representation of the reference profile. That is the one you are calling `.contrast()` on. |
| `alternativeA` | Contains the JSON Compatible Representation of the parameter profile. |
| `health_reports` | Contains a report for every component. The report checks for drift and invalid values. |
| `score_reports` | Contains a report for every score. |

Let's go in a bit more detail about the reports.

### Heath reports

The health reports is a `dict` containing a `<key, value>` pair for every profile component. The `key` is the component's name, the `value` is another `dict`, containing the component report.  The component report contains 2 sub reports: one for distribution drift and one for invalid values. The `outlier_score`'component's report looks as follows.

```python
report["health_reports"]["outlier_score"]
```

```javascript
{
    "drift": {
        "drift": 0.28241497205477956,
        "drift_xvalue": 2819.3040996070686,
        "alert": true,
        "valid": true
    },
    "invalids": {
        "invalids": 0.0,
        "alert": false,
        "valid": true
    }
}
```

Notice all reports have a metric associated with them \(`drift` for drift reports, `invalids` for invalids reports. They also have a valid key, and an alert key. If `valid` is `False`, you can ignore the report. This will happen is there is not enough data to analyse for example.  IF the report is valid, and the metric is over a certain [threshold](contrasting-profiles.md#thresholds-and-tuning), `alert` will be `True`. As an extra, the drift report returns `drift_xvalue`, the location of where the maximum drift was detected. 

### Score reports

Score reports indicate whether something has changed to the profile's scores. In our example there are 2 scores, so there are 2 reports.

```python
report["score_reports"]
```

The output is very similar to the heath reports.

```javascript
    "mae": {
        "diff": 0.7646013516324919,
        "alert": true,
        "valid": true
    },
    "mean_outlier_score": {
        "diff": 0.2737001712801194,
        "alert": true,
        "valid": true
    }
}
```

Scores will have alert True if the value has increased above or dropped below a certain threshold, depending on the [preference of the score](building-house-prices.md#model-scores) \(i.e. do we want the score to be high or low\).

## Thresholds & Tuning

Drift detection can be difficult. You may not want to watch all features or you may want to tolerate a lot more drift for some features than for others. Raymon lets you easily control this using thresholds. The main reason Raymon does not use traditional statistical hypothesis testing to detect drift, is because statistical significance in ML is meaningless. Practical significance is what we want, and what practical significance is will depend on your use case, and the effect size \(i.e. the amount of drift detected\).

If we do not want to get warned about drift, an increase in invalid values or worse scores, we can tune this using thresholds.

```python
thresholds = {
    "components": {
        "outlier_score": {
            "invalids": 0.01,
            "drift": 0.30
        }
    },
    "scores": {
        "mean_outlier_score": 0.30
    }
}
report = profile.contrast(profile_exp, thresholds=thresholds)
```

Now, the specified alerts will be muted:

```python
print(json.dumps(report["health_reports"]["outlier_score"], indent=4))
print(json.dumps(report["score_reports"], indent=4))
```

```javascript
{
    "drift": {
        "drift": 0.28241497205477956,
        "drift_xvalue": 2819.3040996070686,
        "alert": false,
        "valid": true
    },
    "invalids": {
        "invalids": 0.0,
        "alert": false,
        "valid": true
    }
}
{
    "mae": {
        "diff": 0.7646013516324919,
        "alert": true,
        "valid": true
    },
    "mean_outlier_score": {
        "diff": 0.2737001712801194,
        "alert": false,
        "valid": true
    }
}
```

## Wrapping up

In this section we have seen how you can use model profiles to guard agains drift or degrading data and model quality. In the next sections we'll talk about what extractors are currently available in Raymon and how you can implement your own. 

Raymon also supports making your model predictions traceable and debuggable using our \(free version of\) our platform. Check out t[racing predictions](../tracing-predictions/untitled.md) to find out more!





