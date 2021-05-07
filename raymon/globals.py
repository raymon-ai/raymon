from abc import ABC, abstractmethod


class ProfileStateException(Exception):
    pass


class ExtractorException(Exception):
    pass


class DataException(Exception):
    pass


class Serializable(ABC):
    def class2str(self):
        module = str(self.__class__.__module__)
        classname = str(self.__class__.__name__)
        return f"{module}.{classname}"

    @abstractmethod
    def to_jcr(self):
        """Return a JSON compatible representation of the object. Will generally return a dict cintaining the objects state, but can return anything JSON serializable. json.dumps(xxx) will be called on the output xxx of this function."""
        # Return a json-compatible representation
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def from_jcr(cls, jcr):
        """Given the JSON compatible representation from the function above, load an object of this type with the desired state.

        Parameters
        ----------
        jcr : [dict]
            The jcr representation returned from the `to_jcr` function above. Will generally be a dict, but can be anything JSON serializable.

        Returns
        -------
        obj : type(this)
        """
        # Load a json-compatible representation
        raise NotImplementedError()


class Buildable(ABC):
    @abstractmethod
    def build(self, input, output, actual):
        """Your component extractor must be Buildable. This means that it may use data to set some reference values, used to calculate the component to be extracted from a data sample. A good example for this is the `raymon.profiling.extractors.structured.KMeansOutlierScorer` extractor, which clusters the data at building time and saves those clusters as reference in the objects state. If you dont require and buildabe state, like the `raymon.profiling.extractors.structured.ElementExtractor`, don't do anything in this function.

        Parameters
        ----------
        data : any
            The set of data available at building time. Can be any type you want.
        Returns
        -------
        None
        """
        raise NotImplementedError

    @abstractmethod
    def is_built(self):
        """
        Check whether the object has been built. Typically, this method checks whether the required references for the object is set. If your ComponentExtractor does not use any references, simply return True.

        Returns
        -------
        is_built : bool
        """
        raise NotImplementedError
