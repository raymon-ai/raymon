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
        """Extracts a feature from a data instance.

        Parameters
        ----------
        data : any
            The data instance you want to extract a feature from. The type is up to you.

        """
        raise NotImplementedError

    def extract_multiple(self, data):
        if data is None:
            raise DataException(f"{self.name}: Data is None")
        features = []
        if isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray):
            features = self.extract(data)
        elif isinstance(data, Iterable):
            for data in data:
                features.append(self.extract(data))
        else:
            raise DataException("Data should be a DataFrame or Iterable")
        return features


class ScoringExtractor(Extractor):
    @abstractmethod
    def extract(self, output, actual):
        """Extracts a feature from a data instance.

        Parameters
        ----------
        data : any
            The data instance you want to extract a feature from. The type is up to you.

        """
        raise NotImplementedError

    def extract_multiple(self, output, actual):
        if output is None:
            raise DataException(f"{self.name}: output is None")
        if actual is None:
            raise DataException(f"{self.name}: actual is None")
        if type(output) != type(actual):
            raise DataException(f"{self.name}: output and actual not of same type")
        if len(output) != len(actual):
            raise DataException(f"{self.name}: output and actual not of same length")

        features = []
        if isinstance(output, pd.DataFrame) or isinstance(output, np.ndarray):
            features = self.extract(output, actual)
        elif isinstance(output, Iterable):
            for data in output:
                features.append(self.extract(output, actual))
        else:
            raise DataException("Data should be a DataFrame or Iterable")
        return features
