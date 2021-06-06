from PIL import ImageFilter
import numpy as np

from raymon.profiling.extractors import SimpleExtractor


class Sharpness(SimpleExtractor):
    """Measures the blurryness or sharpness of an iamge. Based on
    https://www.pyimagesearch.com/2015/09/07/blur-detection-with-opencv/
    """

    def extract(self, data):
        img = data.convert("L")
        filtered = img.filter(ImageFilter.Kernel((3, 3), (0, 1, 0, 1, -4, 1, 0, 1, 0), scale=1, offset=0))
        return float(np.array(filtered).mean())  # .var())

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
