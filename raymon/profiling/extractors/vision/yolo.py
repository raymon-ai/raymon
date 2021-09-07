import numpy as np

from raymon.profiling.extractors import SimpleExtractor


class YoloConfidenceExtractor(SimpleExtractor):
    def __init__(self, aggregation="mean"):
        self.aggregation = aggregation

    """
    PROPERTIES
    """

    @property
    def aggregation(self):
        return self._aggregation

    @aggregation.setter
    def aggregation(self, value):

        if isinstance(value, str) and value in ["mean", "min"]:
            self._aggregation = value
        else:
            raise ValueError(f"aggregation must be either 'mean', or 'min'")

    """Feature extractor"""

    def extract(self, data):
        # data = boxes
        confidences = data[:, 4]
        if self.aggregation == "mean":
            return float(np.mean(confidences))
        else:
            return float(np.min(confidences))

    """Serializable interface """

    def to_jcr(self):
        data = {
            "aggregation": self.aggregation,
        }
        state = {"class": self.class2str(), "state": data}
        return state

    @classmethod
    def from_jcr(cls, jcr):
        aggregation = "mean"
        if "aggregation" in jcr:
            aggregation = jcr["aggregation"]

        return cls(aggregation=aggregation)

    """Buildable interface"""

    def build(self, data):
        pass

    def is_built(self):
        return True

    def __str__(self):
        return f"{self.class2str()} ({self.aggregation})"
