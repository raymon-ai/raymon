from abc import ABC, abstractmethod
from collections.abc import Iterable

import pandas as pd
import numpy as np

from raymon.globals import Buildable, Serializable, DataException

from raymon.globals import ExtractorException


class Extractor(Serializable, Buildable, ABC):
    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        return str(self)


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
            for data in data:
                components.append(self.extract(data))
        else:
            raise DataException("Data should be a DataFrame or Iterable")
        return components


class ScoringExtractor(Extractor):
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
            components = self.extract(output, actual)
        elif isinstance(output, Iterable):
            for out, act in zip(output, actual):
                components.append(self.extract(out, act))
        else:
            raise DataException("Data should be a DataFrame or Iterable")
        return components
