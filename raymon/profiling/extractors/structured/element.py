import numpy as np

from raymon.globals import DataException, ExtractorException
from raymon.profiling.extractors import Extractor
from raymon.profiling.components import FloatComponent, IntComponent, CategoricComponent


class ElementExtractor(Extractor):
    """
    Extract one element from a vector
    """

    def __init__(self, name, element, path="input"):
        super().__init__(name=name, path=path)
        self.element = element

    """ELEMENT"""

    @property
    def element(self):
        return self._element

    @element.setter
    def element(self, value):
        if not (isinstance(value, str) or isinstance(value, int)):
            raise DataException("element to extract must be int or str")
        self._element = value

    def extract(self, input, output, actual):
        data = self.parse_params(input=input, output=output, actual=actual)
        return data[self.element]

    """Serializable interface """

    def to_jcr(self):
        data = {
            "element": self.element,
        }
        return data

    @classmethod
    def from_jcr(cls, jcr):
        return cls(**jcr)

    """Buildable interface"""

    def build(self, input, output, actual):
        pass

    def is_built(self):
        return True

    def __str__(self):
        return f"{self.__class__.__name__}(element={self.element})"


def generate_components(dtypes, path):
    components = []
    for key in dtypes.index:
        # Check type: Numeric or categoric
        extractor = ElementExtractor(name=key, element=key, path=path)
        if np.issubdtype(dtypes[key], np.floating):
            component = FloatComponent(name=key, extractor=extractor)
        elif np.issubdtype(dtypes[key], np.integer):
            component = IntComponent(name=key, extractor=extractor)
        elif dtypes[key] == np.dtype("O"):
            component = CategoricComponent(name=key, extractor=extractor)
        else:
            raise ValueError(f"dtype {dtypes[key]} not supported.")
        components.append(component)

    return components
