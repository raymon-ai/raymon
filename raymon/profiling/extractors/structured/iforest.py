import base64
import pickle
import io
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline

from sklearn.exceptions import NotFittedError
from raymon.profiling.extractors import SimpleExtractor


class IsolationForestOutlierScorer(SimpleExtractor):
    """
    Builds an isolation forest at building time and generates an outlier score at validation time.
    """

    def __init__(self, iforest):
        self.iforest = iforest

    """
    PROPERTIES
    """

    @property
    def iforest(self):
        return self._iforest

    @iforest.setter
    def iforest(self, value):
        if isinstance(value, IsolationForest) or isinstance(value, Pipeline):
            self._iforest = value
        else:
            raise ValueError(f"iforest must be of type  {IsolationForest}, not {type(value)}")

    def extract(self, data):
        if isinstance(data, pd.Series):
            data = data.to_frame().T
        if len(data.shape) == 1:
            data = data[None, :]
        elif len(data.shape) == 2 and data.shape[0] == 1:
            pass
        else:
            raise ValueError(f"data must be of shape (1, n) or (n, ), not {data.shape}")
        pred = self.iforest.score_samples(data)
        predparsed = pred.tolist()[0]
        return predparsed

    """Buildable interface"""

    def build(self, data):
        # self.iforest.fit(X=data)
        # We do NOT want to build this when building the profile, or it will detect outliers on the current profile dataset.
        pass

    def is_built(self):
        try:
            self.iforest.predict(X=None)
        except NotFittedError:
            return False
        except Exception:
            return True
        return True

    """Serializable interface"""

    def to_jcr(self):
        f = io.BytesIO()
        pickle.dump(self.iforest, f)
        byte_arr = f.getvalue()
        b64 = base64.b64encode(byte_arr).decode()
        data = {"iforest_b64": b64}
        state = {"class": self.class2str(), "state": data}
        return state

    @classmethod
    def from_jcr(cls, jcr):
        iforest_b64 = jcr["iforest_b64"]
        rest_byte_arr = io.BytesIO(base64.decodebytes(iforest_b64.encode()))
        iforest = pickle.load(rest_byte_arr)
        return cls(iforest=iforest)
