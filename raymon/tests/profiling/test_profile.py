#%%
import pytest

import pandas as pd
import numpy as np

from raymon.profiling.extractors.structured import generate_comps
from raymon import CategoricComponent, FloatComponent, IntComponent
from raymon import ModelProfile
from raymon.globals import ProfileStateException, DataException
from raymon import NumericStats, CategoricStats
from raymon.profiling.extractors.structured import ElementExtractor

#%%
def test_constuct_comps():
    pass
    # cols = {
    #     "num1": list(range(10)),
    #     "cat1": ["a"] * 5 + ["b"] * 5,
    #     "cat2": ["c"] * 5 + ["d"] * 5,
    #     "num2": [0.2] * 10,
    # }
    # df = pd.DataFrame(data=cols)
    # components = generate_comps(dtypes=df.dtypes)
    # assert len(components) == 4
    # assert isinstance(components[0], IntComponent)
    # assert isinstance(components[1], CategoricComponent)
    # assert isinstance(components[2], CategoricComponent)
    # assert isinstance(components[3], FloatComponent)
