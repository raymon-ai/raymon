from PIL import ImageFilter
import numpy as np

from raymon.profiling.extractors import Extractor


class Sharpness(Extractor):
    """Measures the blurryness or sharpness of an iamge. Based on
    https://www.pyimagesearch.com/2015/09/07/blur-detection-with-opencv/
    """

    def __init__(self, name, path="input"):
        super().__init__(name=name, path=path)

    def extract(self, input, output, actual):
        data = self.parse_params(input=input, output=output, actual=actual)
        img = data.convert("L")
        filtered = img.filter(ImageFilter.Kernel((3, 3), (0, 1, 0, 1, -4, 1, 0, 1, 0), scale=1, offset=0))
        return float(np.array(filtered).mean())  # .var())

    """Serializable inteface """

    def to_jcr(self):
        return {}

    @classmethod
    def from_jcr(cls, jcr):
        return cls()

    """Buildable interface"""

    def build(self, input, output, actual):
        pass

    def is_built(self):
        return True
