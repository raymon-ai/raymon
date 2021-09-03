import numpy as np
import pandas as pd


def filter_nan(values):
    return [v for v in values if isinstance(v, str) or not np.isnan(v)]
