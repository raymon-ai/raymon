from abc import abstractmethod
from raymon.globals import Serializable, Buildable, DataException
from pydoc import locate

import numpy as np
import pandas as pd


class Score(Serializable, Buildable):
    def __init__(
        self,
        name,
        inputs,
        preference,
        result,
    ):  # str or dict
        """
        [summary]

        Parameters
        ----------
        inputs : list
             [tag_name, tag_name]
        preference : [type]
             {output_name: 'high', output_name: 'low'}
        """
        self.name = name
        self.inputs = inputs
        self.preference = preference
        self.result = result

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError(f"Score name should be a string")
        if "@" in value:
            raise ValueError(f"Score name should not include '@'")
        self._name = value.lower()

    @property
    def inputs(self):
        return self._inputs

    @inputs.setter
    def inputs(self, value):
        if not isinstance(value, list) and all(isinstance(s, str) for s in value):
            raise ValueError(f"Score inputs must be a list of str tag names")
        self._inputs = value

    @property
    def preference(self):
        return self._preference

    @preference.setter
    def preference(self, value):
        if value not in ["low", "high"]:
            raise ValueError(f"Score preference must be either 'high' or 'low'.")
        self._preference = value

    def build(self, data, **kwargs):
        raise NotImplementedError()

    def is_built(self):
        return self.result is not None

    def to_jcr(self):
        return {
            "class": self.class2str(),
            "state": {
                "name": self.name,
                "inputs": self.inputs,
                "preference": self.preference,
                "result": self.result,
            },
        }

    def contrast(self, other, components, threshold=None):
        report = {}
        self_val = self.result
        other_val = other.result
        if self_val is None or other_val is None:
            report = {
                "diff": None,
                "alert": False,
                "valid": False,
            }
        else:
            component = components[self.inputs[0]]
            valuerrange = component.stats.range
            diff = abs(other_val - self_val) / valuerrange
            # If value has decreased, and larger is better
            if self_val > other_val and diff > threshold and self.preference == "high":
                alert = True
            elif self_val < other_val and diff > threshold and self.preference == "low":
                alert = True
            else:
                alert = False
            report = {
                "diff": float(diff),
                "alert": alert,
                "valid": True,
            }
        return report

    @classmethod
    def from_jcr(cls, jcr):
        classpath = jcr["class"]
        state_jcr = jcr["state"]
        statsclass = locate(classpath)
        if statsclass is None:
            raise NameError(f"Could not locate classpath {classpath}")
        return statsclass.from_jcr(state_jcr)


class MeanScore(Score):
    def __init__(self, name, inputs, preference, result=None):
        super().__init__(name, inputs=inputs, preference=preference, result=result)

    def build(self, data):
        tag = self.inputs[0]
        to_reduce = data[tag]
        obs_mean = np.mean(to_reduce)
        self.result = obs_mean

    @classmethod
    def from_jcr(cls, jcr):
        return cls(**jcr)


class PrecisionScore(Score):
    def __init__(self, name, inputs, preference="high", result=None):
        super().__init__(name, inputs=inputs, preference=preference, result=result)

    def build(self, data):
        tag = self.inputs[0]
        to_reduce = data[tag]
        counts = pd.Series(to_reduce).value_counts().to_dict()
        reduced = self.get_precision(counts)
        self.result = reduced

    def get_precision(self, counts):
        result = {}
        for key in ["TP", "FP", "TN", "FN"]:
            if key not in counts:
                counts[key] = 0
        try:
            result = counts["TP"] / (counts["TP"] + counts["FP"])
        except:
            result = -1
        return result

    @classmethod
    def from_jcr(cls, jcr):
        return cls(**jcr)


class RecallScore(Score):
    def __init__(self, name, inputs, preference="high", result=None):
        super().__init__(name, inputs=inputs, preference=preference, result=result)

    def build(self, data):
        tag = self.inputs[0]
        to_reduce = data[tag]
        counts = pd.Series(to_reduce).value_counts().to_dict()
        reduced = self.get_recall(counts)
        self.result = reduced

    def get_recall(self, counts):
        result = {}
        for key in ["TP", "FP", "TN", "FN"]:
            if key not in counts:
                counts[key] = 0
        try:
            result = counts["TP"] / (counts["TP"] + counts["FN"])
        except:
            result = -1
        return result

    @classmethod
    def from_jcr(cls, jcr):
        return cls(**jcr)


class ClassPrecisionScore(Score):
    def __init__(self, name, inputs, preference="high", result=None):
        super().__init__(name, inputs=inputs, preference=preference, result=result)

    def build(self, data):
        prediction_tag = self.inputs[0]
        actual_tag = self.inputs[1]
        preds = data[prediction_tag]

        counts = pd.Series(to_reduce).value_counts().to_dict()
        reduced = self.get_precision(counts)
        self.result = reduced

    def get_precision(self, counts):
        result = {}
        for key in ["TP", "FP", "TN", "FN"]:
            if key not in counts:
                counts[key] = 0
        try:
            result = counts["TP"] / (counts["TP"] + counts["FP"])
        except:
            result = -1
        return result

    @classmethod
    def from_jcr(cls, jcr):
        return cls(**jcr)


class ClassRecallScore(Score):
    def __init__(self, name, inputs, preference="high", result=None):
        super().__init__(name, inputs=inputs, preference=preference, result=result)

    def build(self, data):
        tag = self.inputs[0]
        to_reduce = data[tag]
        counts = pd.Series(to_reduce).value_counts().to_dict()
        reduced = self.get_recall(counts)
        self.result = reduced

    def get_recall(self, counts):
        result = {}
        for key in ["TP", "FP", "TN", "FN"]:
            if key not in counts:
                counts[key] = 0
        try:
            result = counts["TP"] / (counts["TP"] + counts["FN"])
        except:
            result = -1
        return result

    @classmethod
    def from_jcr(cls, jcr):
        return cls(**jcr)


class ElementCorrelationScore(Score):
    pass


class ConfusionMatrixScore(Score):
    pass
