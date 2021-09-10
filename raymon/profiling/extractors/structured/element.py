import numpy as np

from raymon.globals import DataException, ExtractorException
from raymon.profiling.extractors import SimpleExtractor
from raymon.profiling.components import InputComponent, OutputComponent, ActualComponent, DataType


class ElementExtractor(SimpleExtractor):
    """
    This extractor simply extracts an element from an array, series or dict.
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


class MaxScoreElementExtractor(SimpleExtractor):
    """
    Extract the index with the maximum value from a vector, and optionally translate it to a categorical value if categories are given.
    """

    def __init__(self, categories=None):
        self.categories = categories

    """categories"""

    @property
    def categories(self):
        return self._categories

    @categories.setter
    def categories(self, value):
        if value is None:
            self._categories = None
        elif isinstance(value, list):
            self._categories = value
        elif isinstance(value, np.ndarray) and len(value.shape) == 1:
            self._categories = value.tolist()
        else:
            raise DataException("categories must be None, a list or 1D numpy array")

    def extract(self, data):
        idx = np.argmax(data)
        if self.categories is not None:
            return self.categories[idx]
        return idx

    """Serializable interface """

    def to_jcr(self):
        data = {
            "class": self.class2str(),
            "state": {
                "categories": self.categories,
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
        return f"{self.__class__.__name__}(categories={self.categories})"


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
