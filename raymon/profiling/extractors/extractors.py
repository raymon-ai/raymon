from abc import ABC, abstractmethod
from collections.abc import Iterable
from pydoc import locate

import pandas as pd
import numpy as np

from raymon.globals import Buildable, Serializable, DataException

from raymon.globals import ExtractorException


class Extractor(Serializable, Buildable, ABC):
    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        return str(self)

    @classmethod
    def from_jcr(cls, jcr):
        classpath = jcr["class"]
        state_jcr = jcr["state"]
        statsclass = locate(classpath)
        if statsclass is None:
            raise NameError(f"Could not locate classpath {classpath}")
        return statsclass.from_jcr(state_jcr)


class SimpleExtractor(Extractor):
    @abstractmethod
    def extract(self, data):
        """Extracts a component from a data instance.

        Parameters
        ----------
        data : any
            The data instance you want to extract a component from. The type is up to you.

        """
        raise NotImplementedError

    def extract_multiple(self, data):
        if data is None:
            raise DataException(f"Data is None")
        components = []
        if isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray):
            components = self.extract(data)
        elif isinstance(data, Iterable):
            for el in data:
                components.append(self.extract(el))
        else:
            raise DataException("Data should be a DataFrame or Iterable")
        return components


class EvalExtractor(Extractor):
    @abstractmethod
    def extract(self, output, actual):
        """Extracts a component from a data instance.

        Parameters
        ----------
        data : any
            The data instance you want to extract a component from. The type is up to you.

        """
        raise NotImplementedError

    def extract_multiple(self, output, actual):
        if output is None:
            raise DataException("output is None")
        if actual is None:
            raise DataException("actual is None")
        if type(output) != type(actual):
            raise DataException("output and actual not of same type")
        if len(output) != len(actual):
            raise DataException("output and actual not of same length")

        components = []
        if isinstance(output, pd.DataFrame) or isinstance(output, np.ndarray):
            zipped = zip(output, actual)
            for out, act in zipped:
                components.append(self.extract(out, act))
        elif isinstance(output, Iterable):
            zipped = zip(output, actual)
            for out, act in zipped:
                components.append(self.extract(out[0], act[0]))
        else:
            raise DataException("Data should be a DataFrame or Iterable")
        return components


class NoneExtractor(SimpleExtractor):
    def extract(self, data):
        return 0

    def to_jcr(self):
        data = {}
        return data

    @classmethod
    def from_jcr(cls, jcr):
        return cls()

    """Buildable interface"""

    def build(self, data):
        pass

    def is_built(self):
        return True


class NoneEvalExtractor(EvalExtractor):
    def __init__(self, lower_better=True):
        self.lower_better = lower_better

    def extract(self, output, actual):
        return 0

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
