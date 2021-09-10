import numpy as np

from raymon.globals import DataException, ExtractorException
from raymon.profiling.extractors import SimpleExtractor


class ClassificationMarginExtractor(SimpleExtractor):
    """
    Takes the output of a classifier (i.e. a vector of probabilities) and extracts the classification margin, which is the difference in probability between the most likely and the second most likely class.
    """

    def extract(self, data):
        asc = np.sort(data)
        margin = float(1 - (asc[-1] - asc[-2])) ** 2
        return margin

    """Serializable interface """

    def to_jcr(self):
        data = {
            "class": self.class2str(),
            "state": {},
        }
        return data

    @classmethod
    def from_jcr(cls, jcr):
        return cls(**jcr)

    """Buildable interface"""

    def build(self, data):
        pass

    def is_built(self):
        return True

    def __str__(self):
        return f"{self.__class__.__name__}()"
