from abc import ABC, abstractmethod

from raymon.globals import Buildable, Serializable


class Extractor(Serializable, Buildable, ABC):
    @abstractmethod
    def extract(self, data):
        """Extracts a feature from a data instance.

        Parameters
        ----------
        data : any
            The data instance you want to extract a feature from. The type is up to you.

        """
        raise NotImplementedError

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)
