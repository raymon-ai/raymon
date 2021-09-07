---
description: Introduction to ModelProfiles with structured data.
---

# Building: house prices

Allright, let's get started with Raymon by building a so called `ModelProfile`, and then see what we can do with this profile. In Raymon, profiles are used to capture all kinds of data characteristics that you want to watch. These profiles can then be used to validate data, or check for data drift and model performance drops.

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

To monitor our data health and model performance in production, we'll create a model profile. A model profile is a collection on components that each watch a certain characteristic of our data. In this case, we can for example track every input feature for stability. The snippet below shows how to construct a profile that  watches a few input features of various data types \(float, int and a categorical feature\).

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

Lines 12-14 should be repeated for every input feature we want to track. Our model has 60 input features, so this seems a bit cumbersome. Luckily we can use `generate_components` shorthand for this. This will generate an `InputComponent` for every column of our dataframe!

```python
profile = ModelProfile(
    name="HousePricesCheap",
    version="3.0.0",
    components=generate_components(X_test[feature_selector].dtypes, complass=InputComponent)

)
```

After specifying all input features, we can build 





After we have defined the features we want to track, we can build the profile using 

### Extra drift guards

###  

Start by tracking input features, and add an outlier score.

Add output, actual and eval components.

Add a score.

Inspect and build the profile.

