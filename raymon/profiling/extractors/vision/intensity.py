from PIL import Image, ImageFilter
import numpy as np

from raymon.profiling.extractors import Extractor


class AvgIntensity(Extractor):

    _config_attrs = []
    _compile_attrs = []
    _ccable_deps = []
    _attrs = _config_attrs + _compile_attrs + _ccable_deps

    def __init__(self):
        pass

    def extract(self, data):
        img = data
        img = img.convert("L")
        return float(np.array(img).mean())

    """Serializable inteface """

    def to_jcr(self):
        return {}

    @classmethod
    def from_jcr(cls, jcr):
        return cls()

    """Buildable interface"""

    def build(self, data):
        pass

    def is_built(self):
        return True
