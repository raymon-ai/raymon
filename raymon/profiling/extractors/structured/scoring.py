# from raymon.types import load_jcr
from raymon.profiling.extractors import ScoringExtractor


class ClassificationErrorType(ScoringExtractor):
    def __init__(self, positive=1):
        self.positive = positive

    def extract(self, output, actual):
        if actual == self.positive and output == self.positive:
            err = "TP"
        elif actual == self.positive and output != self.positive:
            err = "FN"
        elif actual != self.positive and output == self.positive:
            err = "FP"
        else:
            err = "TN"
        return err

    """Serializable interface """

    def to_jcr(self):
        data = {
            "positive": self.positive,
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


class AbsoluteError(ScoringExtractor):
    def extract(self, output, actual):
        return abs(output - actual)

    """Serializable interface """

    def to_jcr(self):
        data = {}
        return data

    @classmethod
    def from_jcr(cls, jcr):
        return cls(**jcr)

    """Buildable interface"""

    def build(self, data):
        pass

    def is_built(self):
        return True


class SquaredError(ScoringExtractor):
    def extract(self, output, actual):
        return pow(output - actual, 2)

    """Serializable interface """

    def to_jcr(self):
        data = {}
        return data

    @classmethod
    def from_jcr(cls, jcr):
        return cls(**jcr)

    """Buildable interface"""

    def build(self, data):
        pass

    def is_built(self):
        return True
