# from raymon.types import load_jcr
from raymon.profiling.extractors import ScoreExtractor


class ClassificationErrorType(ScoreExtractor):
    def __init__(self, positive=1, lower_better=True):
        super().__init__(lower_better=lower_better)
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
        data = super().to_jcr()
        data["positive"] = self.positive
        return data

    @classmethod
    def from_jcr(cls, jcr):
        return cls(**jcr)

    """Buildable interface"""

    def build(self, data):
        pass

    def is_built(self):
        return True


class AbsoluteError(ScoreExtractor):
    def __init__(self, lower_better=True):
        super().__init__(lower_better=True)

    def extract(self, output, actual):
        return abs(output - actual)

    """Serializable interface """

    def to_jcr(self):
        data = super().to_jcr()
        return data

    @classmethod
    def from_jcr(cls, jcr):
        return cls(**jcr)

    """Buildable interface"""

    def build(self, data):
        pass

    def is_built(self):
        return True


class SquaredError(ScoreExtractor):
    def __init__(self, lower_better=True):
        super().__init__(lower_better=True)

    def extract(self, output, actual):
        return pow(output - actual, 2)

    """Serializable interface """

    def to_jcr(self):
        data = super().to_jcr()
        return data

    @classmethod
    def from_jcr(cls, jcr):
        return cls(**jcr)

    """Buildable interface"""

    def build(self, data):
        pass

    def is_built(self):
        return True
