#%%
# %load_ext autoreload
# %autoreload 2
import copy

#%%
# Building a model
import pandas as pd
from sklearn.model_selection import train_test_split
from raymon.tests.profiling.houseprices_utils import prep_df, train, load_data

cheap_houses_csv = "../raymon/tests/sample_data/houseprices/subset-cheap.csv"
X, y = load_data(cheap_houses_csv)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.5, random_state=1)


rf, coltf, feature_selector_ohe, feature_selector = train(
    X_train=X_train,
    y_train=y_train,
)

Xtf_test = pd.DataFrame(
    coltf.transform(X_test[feature_selector]),
    columns=feature_selector_ohe,
)
Xtf_val = pd.DataFrame(
    coltf.transform(X_val[feature_selector]),
    columns=feature_selector_ohe,
)

y_pred_test = rf.predict(Xtf_test[feature_selector_ohe])
y_pred_val = rf.predict(Xtf_val[feature_selector_ohe])

#%%
[feature_selector[0], feature_selector[6], feature_selector[-1]]

#%%
# Build a modelprofile
from raymon import ModelProfile
from raymon import InputComponent, OutputComponent, ActualComponent, EvalComponent
from raymon import DataType
from raymon.profiling.extractors.structured.element import ElementExtractor, generate_components


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


# %%
profile = ModelProfile(
    name="HousePricesCheap",
    version="3.0.0",
    components=generate_components(X_train[feature_selector].dtypes, complass=InputComponent),
)
profile.build(input=X_val[feature_selector])
# %%
# profile.view()
# %%
jcr = profile.to_jcr()
profile.save(".")
#%%
# Load from disk
loaded = ModelProfile.load("housepricescheap@3.0.0.json")
# Load from the loaded jcr
loaded = ModelProfile.from_jcr(jcr)
# %%
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
    ]
    + generate_components(X_train[feature_selector].dtypes, complass=InputComponent),
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
profile.build(input=X_val[feature_selector], output=y_pred_val[:, None], actual=y_val[:, None])
profile.view()


#%%
# Set domains
domains = {
    "1stflrsf": (0, None),  # Set the minimum to 0
    "2ndflrsf": (None, 2000),  # Set the minimum to 2000
    "3ssnporch": (0, 400),  # Set min and max
    "bldgtype": ["1Fam", "TwnhsE", "Twnhs", "2fmCon"],  # removed "Duplex"
}
profile_lim = copy.deepcopy(profile)
profile_lim.build(input=X_val[feature_selector], output=y_pred_val[:, None], actual=y_val[:, None], domains=domains)
profile_lim.view()

# %%
# profile = ModelProfile.load("housepricescheap@3.0.0.json")
request = X_test[feature_selector].iloc[0, :]
tags = profile.validate_input(request)
# filter_errors(tags)
tags
#%%
from raymon.tags import filter_errors

invalid = X_test[feature_selector].iloc[0, :].copy()
# Some weird value
invalid["1stFlrSF"] = 10000
tags = profile.validate_input(invalid)
filter_errors(tags)

#%%
from raymon.tags import flatten_jcr

profile.view(poi=tags)
#%%
tags_flat = flatten_jcr(tags)
profile.view(poi=tags_flat)

#%%
request_actual = y_test.iloc[0:1]
request_pred = rf.predict(coltf.transform(request.to_frame().T))

output_tags = profile.validate_output(request_pred[:, None])
actual_tags = profile.validate_actual(request_actual[:, None])
eval_tags = profile.validate_eval(output=request_pred[:, None], actual=request_actual[:, None])
# or all at once:
all_tags = profile.validate_all(input=request, output=request_pred[:, None], actual=request_actual[:, None])

# %%
exp_houses_csv = "../raymon/tests/sample_data/houseprices/subset-exp.csv"
X_exp_test, y_exp_test = load_data(exp_houses_csv)
Xtf_exp_test = pd.DataFrame(
    coltf.transform(X_exp_test[feature_selector]),
    columns=feature_selector_ohe,
)

y_exp_pred = rf.predict(Xtf_exp_test[feature_selector_ohe])

#%%
import copy

profile_exp = copy.deepcopy(profile)
profile_exp.name = "HousePricesExp"
profile_exp.version = "3.0.0"
profile_exp.build(
    input=X_exp_test[feature_selector], output=y_exp_pred[:, None], actual=y_exp_test[:, None], build_extractors=False
)
profile_exp.view()
#%%
profile.view_contrast(profile_exp)

#%%
# Compare this with a profile of the same distribution, but unseen data
profile_cheap_new = copy.deepcopy(profile)
profile_cheap_new.name = "HousePricesCheapNew"
profile_cheap_new.version = "3.0.0"
profile_cheap_new.build(
    input=X_test[feature_selector], output=y_pred_test[:, None], actual=y_test[:, None], build_extractors=False
)
# profile_cheap_new.view()
profile.view_contrast(profile_cheap_new)

# %%
# %%
report = profile.contrast(profile_exp)
import json

print(json.dumps(report["component_reports"]["outlier_score"], indent=4))
# %%
profile.view_contrast(profile_exp)

# %%
report_same = profile.contrast(profile_cheap_new)
print(json.dumps(report_same["global_reports"]["scores"], indent=4))  # Eh-oh, not good.

#%%
thresholds = {
    "components": {"outlier_score": {"invalids": 0.01, "drift": 0.30}},
    "scores": {"mean_outlier_score": 0.30},
}
report = profile.contrast(profile_exp, thresholds=thresholds)
print(json.dumps(report["component_reports"]["outlier_score"], indent=4))
print(json.dumps(report["global_reports"]["scores"], indent=4))

# %%
