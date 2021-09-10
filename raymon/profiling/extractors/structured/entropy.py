import numpy as np
from scipy.stats import entropy
from raymon.globals import DataException, ExtractorException
from raymon.profiling.extractors import SimpleExtractor


class ClassificationEntropyExtractor(SimpleExtractor):
    """
    Takes the output of a classifier (i.e. a vector of probabilities) and extracts the entropy.
    """

    def extract(self, data):
        h = float(entropy(data))
        return h

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
