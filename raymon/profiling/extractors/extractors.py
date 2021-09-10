from abc import ABC, abstractmethod
from collections.abc import Iterable
from pydoc import locate
import pickle
import io
import base64
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
        if isinstance(data, pd.DataFrame):
            components = data.apply(self.extract, axis="columns", raw=False).tolist()
        elif isinstance(data, Iterable) or isinstance(data, np.ndarray):
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
        if isinstance(output, pd.Series) or isinstance(output, np.ndarray):
            for i in range(len(output)):
                out = output[i]
                act = actual[i]
                components.append(self.extract(out, act))
        elif isinstance(output, pd.DataFrame):
            for i in range(len(output)):
                out = output.iloc[i, :]
                act = actual.iloc[i, :]
                components.append(self.extract(out, act))
            # components = self.extract(output=output, actual=actual)
        elif isinstance(output, Iterable):
            zipped = zip(output, actual)
            for out, act in zipped:
                components.append(self.extract(out[0], act[0]))
        else:
            raise DataException("Data should be a DataFrame or Iterable")
        return components


class SequenceSimpleExtractor(SimpleExtractor):
    """
    Allows you to run preprocessing before running an extractor.

    Parameters
    ----------
    SimpleExtractor : [type]
        [description]
    """

    def __init__(self, prep, extractor, func="transform"):
        """
        Parameters
        ----------
        prep : Object
            Object on which the preprocessing will be called.
        func : str, optional
            The function to call on the prep object. This method will be called with the data as parameter.
        extractor : SimpleExtractor
            The extractor to call after prerpocessing.

        """
        self.prep = prep
        self.extractor = extractor
        self.func = func

    @property
    def prep(self):
        return self._prep

    @prep.setter
    def prep(self, value):
        self._prep = value

    @property
    def func(self):
        return self._func

    @func.setter
    def func(self, value):
        if isinstance(value, str) and hasattr(self.prep, value) and callable(getattr(self.prep, value)):
            self._func = value
        else:
            raise ValueError(f"func should be a string representing the name of a callable attribute of prep.")

    @property
    def extractor(self):
        return self._extractor

    @extractor.setter
    def extractor(self, value):
        if isinstance(value, SimpleExtractor):
            self._extractor = value
        else:
            raise ValueError(f"extractor should be a SimpleExtractor")

    def to_jcr(self):
        f = io.BytesIO()
        pickle.dump(self.prep, f)
        byte_arr = f.getvalue()
        prep_dumped = base64.b64encode(byte_arr).decode()

        return {
            "class": self.class2str(),
            "state": {
                "prep": prep_dumped,
                "func": self.func,
                "extractor": self.extractor.to_jcr(),
            },
        }

    @classmethod
    def from_jcr(cls, jcr):
        prep_b64 = jcr["prep"]
        rest_byte_arr = io.BytesIO(base64.decodebytes(prep_b64.encode()))
        prep = pickle.load(rest_byte_arr)
        func = jcr["func"]
        extr_jcr = jcr["extractor"]
        seq_extr_class = locate(extr_jcr["class"])
        extractor = seq_extr_class.from_jcr(extr_jcr["state"])

        return cls(prep=prep, func=func, extractor=extractor)

    def preprocess(self, data):
        prep_func = getattr(self.prep, self.func)
        if isinstance(data, pd.Series):
            data = data.to_frame().T
        preprocessed = prep_func(data)
        return preprocessed

    def extract(self, data):
        """Extracts a component from a data instance.

        Parameters
        ----------
        data : any
            The data instance you want to extract a component from. The type is up to you.

        """
        preprocessed = self.preprocess(data)
        return self.extractor.extract(data=preprocessed)

    def build(self, data):
        preprocessed = self.preprocess(data)
        self.extractor.build(preprocessed)

    def is_built(self):
        # evalextractor built?
        extr_built = self.extractor.is_built()
        return extr_built and self.prep is not None and self.func is not None


class SequenceEvalExtractor(EvalExtractor):
    """
    Allows you to run preprocessing before running an EvalExtractor.
    """

    def __init__(self, prep_output, prep_actual, eval_extractor):
        """

        Parameters
        ----------
        prep_output : SimpleExtractor
            preprocessing to run for the output element
        prep_actual : SimpleExtractor
            preprocessing to run for the output element
        eval_extractor : EvalExtractor
            The EvalExtractor to run after preprocessing.
        """
        self.prep_output = prep_output
        self.prep_actual = prep_actual
        self.eval_extractor = eval_extractor

    @property
    def prep_output(self):
        return self._prep_output

    @prep_output.setter
    def prep_output(self, value):
        if isinstance(value, list) and all(isinstance(el, SimpleExtractor) for el in value):
            self._prep_output = value
        else:
            raise ValueError(f"value should be a list of SimpleExtractors")

    @property
    def prep_actual(self):
        return self._prep_actual

    @prep_actual.setter
    def prep_actual(self, value):
        if isinstance(value, list) and all(isinstance(el, SimpleExtractor) for el in value):
            self._prep_actual = value
        else:
            raise ValueError(f"value should be a list of SimpleExtractors")

    @property
    def eval_extractor(self):
        return self._eval_extractor

    @eval_extractor.setter
    def eval_extractor(self, value):
        if isinstance(value, EvalExtractor):
            self._eval_extractor = value
        else:
            raise ValueError(f"value should be an EvalExtractors")

    def to_jcr(self):
        output_extractors_jcr = [el.to_jcr() for el in self.prep_output]
        actual_extractors_jcr = [el.to_jcr() for el in self.prep_actual]

        return {
            "class": self.class2str(),
            "state": {
                "prep_output": output_extractors_jcr,
                "prep_actual": actual_extractors_jcr,
                "eval_extractor": self.eval_extractor.to_jcr(),
            },
        }

    @classmethod
    def from_jcr(cls, jcr):
        def load_jcr(jcr):
            seq_extr_class = locate(jcr["class"])
            loaded = seq_extr_class.from_jcr(jcr["state"])
            return loaded

        output_jcrs = jcr["prep_output"]
        prep_output = [load_jcr(jcr) for jcr in output_jcrs]
        actual_jcrs = jcr["prep_actual"]
        prep_actual = [load_jcr(jcr) for jcr in actual_jcrs]
        eval_extractor = load_jcr(jcr["eval_extractor"])

        return cls(
            prep_output=prep_output,
            prep_actual=prep_actual,
            eval_extractor=eval_extractor,
        )

    def extract(self, output, actual):
        """Extracts a component from a data instance.

        Parameters
        ----------
        data : any
            The data instance you want to extract a component from. The type is up to you.

        """
        output_extr = output
        actual_extr = actual
        for extr in self.prep_output:
            output_extr = extr.extract(data=output_extr)

        for extr in self.prep_actual:
            actual_extr = extr.extract(data=actual_extr)
        print(f"output: ")
        print(output_extr)
        print("actual")
        print(actual_extr)
        return self.eval_extractor.extract(output=output_extr, actual=actual_extr)

    def build(self, data):
        pass  # Do not support building for now. KISS

    def is_built(self):
        # preps built?
        out_seq = all(extr.is_built() for extr in self.prep_output)
        act_seq = all(extr.is_built() for extr in self.prep_actual)
        # evalextractor built?
        eval_built = self.eval_extractor.is_built()
        return out_seq and act_seq and eval_built


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
