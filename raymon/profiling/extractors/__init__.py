from abc import ABC, abstractmethod
from collections.abc import Iterable

import pandas as pd
import numpy as np

from raymon.globals import Buildable, Serializable, DataException

from raymon.globals import ExtractorException


class Extractor(Serializable, Buildable, ABC):
    def __init__(self, name, path):
        self.name = name
        self.path = path

    @abstractmethod
    def extract(self, input, output, actual):
        """Extracts a feature from a data instance.

        Parameters
        ----------
        data : any
            The data instance you want to extract a feature from. The type is up to you.

        """
        raise NotImplementedError

    def extract_multiple(self, input, output, actual):
        data = self.parse_params(input, output, actual)
        features = []
        if isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray):
            features = self.extract(input, output, actual)
        elif isinstance(data, Iterable):
            for data in data:
                features.append(self.extract(input, output, actual))
        else:
            raise DataException("Data should be a DataFrame or Iterable")
        return features

    def parse_params(self, input, output, actual):
        if self.path == "input":
            data = input
        elif self.path == "output":
            data = output
        elif self.path == "actual":
            data = actual
        else:
            raise ExtractorException(f"{self.name}: Unknown path specified")
        if data is None:
            raise DataException(f"{self.name}: Path leads to parameter that is None")
        return data

    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"

    def __repr__(self):
        return str(self)
