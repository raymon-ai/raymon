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

Notice that we pass the `build_extractors=False` flag. This makes sure we do not rebuild the extractors. One of the extractors is an outlier detector, which needs to be trained on the original data of course.

When viewing the profile, it should look similar as before. But, now that we have 2 profiles, we can contrast them against each other!

```python
profile.view_contrast(profile_exp)
```

This gives us a the following view, where the original profile is displayed in grey, and the new one in blue. This allows us to spot differences easily. We'll go over different areas of interest below the image.

![Contrasting profiles](../.gitbook/assets/image%20%287%29.png)

### Data integrity

For every component, the next to last columns shows the amount of invalid values encountered in the data when building the profile. Remember, invalid values can be Nones, NaN or out-of-domain values. The invalids columns shows the percentage invalids in the original profile, the percentage in the new profile and the change in percentage points. By clicking the arrows you can easily sort by percentage point change.

### Drift

The drift columns shows how much the data distributions have changed. In the image above, the column has been sorted from high to low. The distance is always between 0% and 100% and is the distance between the 90% confidence intervals of the distributions. For categorical data, the Chebyshev distance is used. For numerical data, we use the same distance metric as in the Kolmogorov-Smirnov test: the maximum distance between the CDF distributions. 

### Scores

Lastly, we also see the difference between the model scores. Here, we see that the mean average error the model made has increased dramatically between the 2 profiles. The outlier score is also much higher on average. 

![The average error has dramatically increased, and so has the average outlier score.](../.gitbook/assets/image%20%286%29.png)

Going from the many warning signals we have, we can conclude something is wrong with our data. We don't get a lot on invalid values, but something in the distribution has certainly changed, and our model is not performing well because of it. 

![The actuals tab shows reveals is wrong here](../.gitbook/assets/image%20%289%29.png)

After inspecting the output and actual tabs of the component views, it should be clear what is wrong here. What happened is that, apparently, our system has been processing houses in a higher price range than what we have seen during training, and our model is struggling with that. Time to retrain your model with new and more relevant data!

## Warning reports

Instead of visualising the drift report, you may only be interested in getting warnings. You can get a report by calling `profile.contrast()`

```python
profile.contrast(profile_exp)
```

This will output a dictionary with the following keys.

| Key | Description |
| :--- | :--- |
| `reference` | Contains the JSON Compatible Representation of the reference profile. That is the one you are calling `.contrast()` on. |
| `alternativeA` | Contains the JSON Compatible Representation of the parameter profile. |
| `health_reports` | Contains a report for every component. The report checks for drift and invalid values. |
| `score_reports` | Contains a report for every score. |

## Thresholds & Tuning

Drift detection can be difficult. You may not want to watch all features or you may want to tolerate a lot more drift for some features than for others. Raymon allows you to easily 

WIP

* How to set & pass them
* How drift is calculated and why: tunability

