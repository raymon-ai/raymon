from abc import abstractmethod
from raymon.globals import Serializable, Buildable, DataException
from pydoc import locate

import numpy as np
import pandas as pd


class Reducer(Serializable, Buildable):
    def __init__(
        self,
        name,
        inputs,
        preferences,
        results=None,
    ):  # str or dict
        """
        [summary]

        Parameters
        ----------
        inputs : list
             [tag_name, tag_name]
        preferences : [type]
             {output_name: 'high', output_name: 'low'}
        """
        self.name = name
        self.inputs = inputs
        self.preferences = preferences
        self.results = results

    def build(self, data, **kwargs):
        raise NotImplementedError()

    def is_built(self):
        return self.results is not None

    def to_jcr(self):
        return {
            "class": self.class2str(),
            "state": {
                "name": self.name,
                "inputs": self.inputs,
                "preferences": self.preferences,
                "results": self.results,
            },
        }

    def contrast(self, other, thresholds=None):
        reports = {}
        for key in self.results:
            if key not in other.results:
                print(f"{key} not found in other profile reducer {self.name}. Skipping.")
                continue
            self_val = self.results[key]
            other_val = other.results[key]
            diff = abs(other_val - self_val) / self_val
            threshold = thresholds.get(key, 0.01)
            # If value has decreased, and larger is better
            if self_val > other_val and diff > threshold and self.preferences[key] == "high":
                alert = True
            elif self_val < other_val and diff > threshold and self.preferences[key] == "low":
                alert = True
            else:
                alert = False
            key_report = {
                "diff": float(diff),
                "alert": alert,
                "valid": True,
            }
            reports[key] = key_report
        return reports

    @classmethod
    def from_jcr(cls, jcr):
        classpath = jcr["class"]
        state_jcr = jcr["state"]
        statsclass = locate(classpath)
        if statsclass is None:
            raise NameError(f"Could not locate classpath {classpath}")
        return statsclass.from_jcr(state_jcr)


class MeanReducer(Reducer):
    def __init__(self, name, inputs, preferences, results=None):
        super().__init__(name, inputs=inputs, preferences=preferences, results=results)

    def build(self, data):
        reduced = {}
        for tag in self.inputs:
            to_reduce = data[tag]
            reduced[tag] = np.mean(to_reduce)
        self.results = reduced

    @classmethod
    def from_jcr(cls, jcr):
        return cls(**jcr)


class PrecisionRecallReducer(Reducer):
    def __init__(self, name, inputs, preferences={"precision": "high", "recall": "high", "f1": "high"}, results=None):
        super().__init__(name, inputs=inputs, preferences=preferences, results=results)

    def build(self, data):
        reduced = {}
        for tag in self.inputs:
            to_reduce = data[tag]
            counts = pd.Series(to_reduce).value_counts().to_dict()
            metrics = self.get_precision_recall(counts)
            reduced[tag] = metrics
        self.results = reduced

    def get_precision_recall(self, counts):
        results = {}
        for key in ["TP", "FP", "TN", "FN"]:
            if key not in counts:
                counts[key] = 0
        try:
            results["precision"] = counts["TP"] / (counts["TP"] + counts["FP"])
        except:
            results["precision"] = -1
        try:
            results["recall"] = counts["TP"] / (counts["TP"] + counts["FN"])
        except:
            results["recall"] = -1
        try:
            results["f1"] = counts["TP"] / (counts["TP"] + 0.5 * (counts["FP"] + counts["FN"]))
        except:
            results["f1"] = -1
        return results

    @classmethod
    def from_jcr(cls, jcr):
        return cls(**jcr)


class ClassErrorReducer(Reducer):
    def __init__(self, name, inputs, preferences={"TP": "high", "FP": "low", "TN": "high", "FN": "low"}, results=None):
        super().__init__(name, inputs=inputs, preferences=preferences, results=results)

    def build(self, data):
        reduced = {}
        for tag in self.inputs:
            to_reduce = data[tag]
            series = pd.Series(to_reduce)
            series = series.where(series.isin(self.preferences.keys()))
            counts = series.value_counts()
            counts = counts / counts.sum()
            frequencies = counts.to_dict()
            parsed = {}

            for key in ["TP", "FP", "TN", "FN"]:
                if key in frequencies:
                    parsed[key.upper()] = float(frequencies[key])
                else:
                    parsed[key.upper()] = 0
            reduced[tag] = parsed
        self.results = reduced

    @classmethod
    def from_jcr(cls, jcr):
        return cls(**jcr)


class ElementCorrelationReducer(Reducer):
    pass


class ConfusionMatrixReducer(Reducer):
    pass
