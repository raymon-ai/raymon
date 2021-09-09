---
description: Introduction to ModelProfiles with structured data.
---

# Building a profile: structured data

Allright, let's get started with Raymon by building a so called `ModelProfile`, and then see what we can do with this profile. This section introduces the basic concepts of Raymon profiling for structured data. The next page will be about computer vision. We recommend reading through this page even though you might be mainly interested in computer vision.

## Prerequisites: data and a model

For this tutorial, we will use the[ house prices dataset](https://www.kaggle.com/c/house-prices-advanced-regression-techniques/data) from Kaggle. A slightly preprocessed version is available in the [test same data](https://github.com/raymon-ai/raymon/tree/master/raymon/tests/sample_data/houseprices) of the library on Github. We'll skip talking too much about the dataset and the model here, but feel free to explore it yourself. In this tutorial's use case, your task is to develop a system that predicts house prices based on some input features.

We can start by building a simple model to predict the house prices. The library tests contain some helper code to train a very basic random forest regressor based on the sample data. The code below trains and returns a [`sklearn.ensemble.RandomForestRegressor`](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html) model, a [`sklearn.compose.ColumnTransformer`](https://scikit-learn.org/stable/modules/generated/sklearn.compose.ColumnTransformer.html) and 2 feature selectors, to select the right columns from the dataset DataFrame before and after one-hot encoding of categorical features. Afterwards, it uses the model to make predictions on our test set, which we'll use below.

```python
import pandas as pd
from raymon.tests.profiling.houseprices_utils import prep_df, train, load_data

cheap_houses_csv = "../raymon/tests/sample_data/houseprices/subset-cheap.csv"
X_train, y_train = load_data(cheap_houses_csv) 
# We use the same train / test data for this test
X_test, y_test = X_test, y_test

rf, coltf, feature_selector_ohe, feature_selector = train(
    X_train=X_train, 
    y_train=y_train,
    )

Xtf_test = pd.DataFrame(
    coltf.transform(X_test[feature_selector]),
    columns=feature_selector_ohe,
)

y_pred = rf.predict(Xtf_test[feature_selector_ohe])
```

## Watching input features

We have trained a model. Good. But now we need to ship it to production and we need to know how it performs in production right? Is the data it processes healthy? Are the predictions still accurate enough 5 month after deployment? Does this new customer that sales has signed get the performance that was advertised? These kinds of questions is what Raymon helps you answer. 

To monitor our data health and model performance in production, we'll create a model profile. A model profile is a collection on components that each watch a certain characteristic of our data. These characteristics are extracted from your data by so called extractors. In this case, we can for example track every input feature for stability. 

The snippet below shows how to construct a profile that  watches a few input features of various data types \(float, int and a categorical feature\). Every component has a name, a datatype and an extractor. The extractor extracts a value from the data, the component analyses the characteristics of those extracted values.

```python
from raymon import ModelProfile
from raymon import InputComponent, OutputComponent, ActualComponent, EvalComponent
from raymon import DataType

from raymon.profiling.extractors.structured.element import ElementExtractor


profile = ModelProfile(
    name="HousePricesCheap",
    version="3.0.0",
    components=[
        InputComponent(name="MSSubClass", extractor=ElementExtractor("MSSubClass"), dtype=DataType.FLOAT),
        InputComponent(name="MasVnrArea", extractor=ElementExtractor("MasVnrArea"), dtype=DataType.INT),
        InputComponent(name="SaleCondition", extractor=ElementExtractor("SaleCondition"), dtype=DataType.CAT),
        # Repeat all input features. Cumbersome right?
    ],
)
```

Lines 12-14 should be repeated for every input feature we want to track. Our model has 60 input features, so this seems a bit cumbersome. Luckily we can use `generate_components` shorthand for this. This will generate an `InputComponent` for every column of our dataframe, and infer the data type automatically.

```python
profile = ModelProfile(
    name="HousePricesCheap",
    version="3.0.0",
    components=generate_components(X_test[feature_selector].dtypes, complass=InputComponent)

)
```

After specifying all input features, we can build the profile by passing it some data. 

```python
profile.build(input=X_test[feature_selector])
```

When building a profile, the data you pass it is analysed, and the profile will save stats like min, max, mean, domain and distribution for every component.

## Viewing profiles

After building a profile, you can view it:

```python
profile.view()
```

This will open a new browser tab and display an interactive visualisation that you can interact with.

![Viewing a ModelProfile](../.gitbook/assets/image%20%281%29.png)

You can also save the model to JSON, or simply convert it into a JSON compatible representation:

```python
# Conver to a JSON compatible representation
profile.to_jcr()
# Save to current directory
profile.save(".")
```

Loading the profile from JSON can be done as follows:

```python
# Load from disk
loaded = ModelProfile.load("housepricescheap@3.0.0.json")
# Load from the loaded jcr
loaded = ModelProfile.from_jcr(jcr)
```

## Extending the profile

Up to now, we only have a very basic profile that watches the input features. We want to watch other things though: the model's outputs, the incoming actuals \(we assume we'll have incoming actuals in production here\) and our model's performance.

### Model Output

We can add an `OutputComponent` that watches our models predictions by simply appending it to the components list. Defining the component goes as follows: we define a component of type `OutputComponent` and pass it an extractor that extracts the first element from the model's output \(that we will pass to it later\).

```python
OutputComponent(name="prediction", extractor=ElementExtractor(element=0))
```

### Model Actual

Watching a model actual is very similar to watching the output, but we need to use a component of type `ActualComponent`here.

```python
ActualComponent(name="actual", extractor=ElementExtractor(0), dtype=DataType.CAT),
```



### Model Evaluations

The last type of component is an `EvalComponent`. `EvalComponents` allow you to combine a model output with the associated actual and let you compute an error metric like the absolute error, classification error type and much more. For now, let's watch the prediction absolute error.

```python
EvalComponent(name="abs_error", extractor=AbsoluteRegressionError())
```

### Data Novelty

In the first part of this section we added watchers for all input features. However, we would like to have an extra check that scores data on how "novel" it is. For that, we can add another `InputComponent`, but we will now use a simple `ElementExtractor` now, but use a `KMeansOutlierScorer`. This `KMeansOutlierScorer` will cluster our input data at build time, and analyse the distance of data to those clusters at evaluation time.

```python
InputComponent(
    name="outlier_score",
    extractor=SequenceSimpleExtractor(prep=coltf, extractor=KMeansOutlierScorer()),
)
```

Notice there is a small caveat here: we wrap our main extractor in a `SequenceSimpleExtractor`. This type of extractor allows us to define a preprocessing step, that will be executed before the specified extractor is called. We use this to transform our input data \(which can have categorical features\) into a purely numeric array, where categorical features are one-hot encoded. We need to do this because the `KMeansOutlierScorer` expects purely numeric values.

### Model Scores

A last thing we can add to our ModelProfile are scores. Scores are single values that indicate how good your data is or how well you model performs. We will add 2 scores: one taking the average absolute error of our predictions, and one taking the average of our outlier score defined in the previous section. We'll also put everything together here.

```python
from raymon.profiling.extractors.structured.scoring import AbsoluteRegressionError
from raymon.profiling import MeanScore
from raymon.profiling.extractors.structured import KMeansOutlierScorer
from raymon.profiling.extractors import SequenceSimpleExtractor


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
```

As you can see, scores take in one extracted feature and aggregate it in a single value. We also pass a preference for this score: in this case we want both scores to be low. Low is good. In a classification context, we could  for example calculate the precision or recall of our model. In that case, we want those score to be high.

Line 32 builds the profile. Since we have defined output, actual and evaluation components, we need to pass output and actual data here too in order to build the full profile.

## Inspecting the full profile

When we build and inspect the full profile, we can see some stuff has been added. We have an easy overview of the scores, and the tabs for outputs, actuals and evaluations also have components associated with them now.

![](../.gitbook/assets/full_profile.gif)

## Wrapping up

We have now built a model profile for structured data. The next section will show how to do this for vision data. If you are not interested in vision at this point, feel free to skip that section. Afterwards, we'll show how we can use these profiles for data [validation](validating-data.md) and [monitoring](contrasting-profiles.md).

