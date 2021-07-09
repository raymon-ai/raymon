from PIL import Image, ImageFilter
import numpy as np

from raymon.profiling.extractors import SimpleExtractor


class AvgIntensity(SimpleExtractor):

    _attrs = []

    def extract(self, data):
        img = data.convert("L")
        return float(np.array(img).mean())

    """Serializable inteface """

    def to_jcr(self):
        state = {"class": self.class2str(), "state": {}}
        return state

    @classmethod
    def from_jcr(cls, jcr):
        return cls()

    """Buildable interface"""

    def build(self, data):
        pass

    def is_built(self):
        return True
