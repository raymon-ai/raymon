import numpy as np

from raymon.globals import DataException, ExtractorException
from raymon.profiling.extractors import SimpleExtractor
from raymon.profiling.components import InputComponent, OutputComponent, ActualComponent, DataType


class ElementExtractor(SimpleExtractor):
    """
    Extract one element from a vector
    """

    def __init__(self, element):
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

    def extract(self, data):
        return data[self.element]

    """Serializable interface """

    def to_jcr(self):
        data = {
            "class": self.class2str(),
            "state": {
                "element": self.element,
            },
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
        return f"{self.__class__.__name__}(element={self.element})"


def generate_components(dtypes, complass=InputComponent, name_prefix=""):
    components = []
    for key in dtypes.index:
        # Check type: Numeric or categoric
        extractor = ElementExtractor(element=key)
        if np.issubdtype(dtypes[key], np.floating):
            component = complass(name=f"{name_prefix}{key}", extractor=extractor, dtype=DataType.FLOAT)
        elif np.issubdtype(dtypes[key], np.integer):
            component = complass(name=f"{name_prefix}{key}", extractor=extractor, dtype=DataType.INT)
        elif dtypes[key] == np.dtype("O"):
            component = complass(name=f"{name_prefix}{key}", extractor=extractor, dtype=DataType.CAT)
        else:
            raise ValueError(f"dtype {dtypes[key]} not supported.")
        components.append(component)

    return components
