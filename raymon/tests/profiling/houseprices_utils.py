#%%
# %load_ext autoreload
# %autoreload 2
# Import packages
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor


to_drop = [
    "Alley",
    "PoolQC",
    "Fence",
    "MiscFeature",
    "BsmtQual",
    "BsmtCond",
    "BsmtExposure",
    "BsmtFinType1",
    "BsmtFinType2",
    "GarageType",
    "GarageFinish",
    "GarageQual",
    "FireplaceQu",
    "GarageCond",
    "Utilities",
    "RoofMatl",
    "Heating",
    "GarageYrBlt",
    "LotFrontage",
]


def load_data(fpath):
    target_col = "SalePrice"
    df = pd.read_csv(fpath, index_col=False)
    df = df.set_index("Id", drop=False)
    X = df.drop([target_col], axis="columns").drop(to_drop, axis="columns", errors="ignore")
    y = df[target_col]
    return X, y


# %%
def get_feature_selectors(X_train):
    no_id = list(X_train.drop("Id", axis="columns").columns)
    # Select categorical features
    cat_columns = list(X_train[no_id].select_dtypes(include=["object"]))
    # Select numeric features
    num_columns = list(X_train[no_id].select_dtypes(exclude=["object"]))
    feature_selector = num_columns + cat_columns
    return feature_selector, cat_columns, num_columns


def build_prep(num_columns, cat_columns):
    # For categorical features: impute missing values as 'UNK', onehot encode
    cat_pipe = make_pipeline(
        SimpleImputer(strategy="constant", fill_value="UNK", verbose=1),
        OneHotEncoder(sparse=False, handle_unknown="ignore"),  # May lead to silent failure!
    )
    # For numerical features: impute missing values as -1
    num_pipe = make_pipeline(
        SimpleImputer(strategy="constant", fill_value=-1, verbose=1),
    )

    coltf = ColumnTransformer(transformers=[("num", num_pipe, num_columns), ("cat", cat_pipe, cat_columns)])
    return coltf


def prep_df(X_train, cat_columns, num_columns, feature_selector):
    coltf = build_prep(num_columns=num_columns, cat_columns=cat_columns)
    # train preprocessor
    Xtf_train = coltf.fit_transform(X_train[feature_selector])
    cat_columns_ohe = list(coltf.transformers_[1][1]["onehotencoder"].get_feature_names(cat_columns))
    # Save the order and name of features
    feature_selector_ohe = num_columns + cat_columns_ohe
    # Transform X_train and make sure features are in right order
    Xtf_train = pd.DataFrame(Xtf_train, columns=feature_selector_ohe)
    return Xtf_train, coltf, feature_selector_ohe


def train(X_train, y_train):
    # Setup preprocessing
    feature_selector, cat_columns, num_columns = get_feature_selectors(X_train)
    Xtf_train, coltf, feature_selector_ohe = prep_df(
        X_train=X_train,
        cat_columns=cat_columns,
        num_columns=num_columns,
        feature_selector=feature_selector,
    )

    # Train
    rf = RandomForestRegressor(n_estimators=25)
    rf.fit(Xtf_train, y_train)
    return rf, coltf, feature_selector_ohe, feature_selector
