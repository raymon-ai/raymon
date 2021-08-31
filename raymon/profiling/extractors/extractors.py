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
        if isinstance(data, pd.DataFrame):
            # components = self.extract(data)
            components = data.apply(self.extract, axis="columns").tolist()
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


class SequenceEvalExtractor(EvalExtractor):
    def __init__(self, sequence_output, sequence_actual, eval_extractor):
        self.sequence_output = sequence_output
        self.sequence_actual = sequence_actual
        self.eval_extractor = eval_extractor

    @property
    def sequence_output(self):
        return self._sequence_output

    @sequence_output.setter
    def sequence_output(self, value):
        if isinstance(value, list) and all(isinstance(el, SimpleExtractor) for el in value):
            self._sequence_output = value
        else:
            raise ValueError(f"value should be a list of SimpleExtractors")

    @property
    def sequence_actual(self):
        return self._sequence_actual

    @sequence_actual.setter
    def sequence_actual(self, value):
        if isinstance(value, list) and all(isinstance(el, SimpleExtractor) for el in value):
            self._sequence_actual = value
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
        output_extractors_jcr = [el.to_jcr() for el in self.sequence_output]
        actual_extractors_jcr = [el.to_jcr() for el in self.sequence_actual]

        return {
            "class": self.class2str(),
            "state": {
                "sequence_output": output_extractors_jcr,
                "sequence_actual": actual_extractors_jcr,
                "eval_extractor": self.eval_extractor.to_jcr(),
            },
        }

    @classmethod
    def from_jcr(cls, jcr):
        def load_jcr(jcr):
            seq_extr_class = locate(jcr["class"])
            loaded = seq_extr_class.from_jcr(jcr["state"])
            return loaded

        output_jcrs = jcr["sequence_output"]
        sequence_output = [load_jcr(jcr) for jcr in output_jcrs]
        actual_jcrs = jcr["sequence_actual"]
        sequence_actual = [load_jcr(jcr) for jcr in actual_jcrs]
        eval_extractor = load_jcr(jcr["eval_extractor"])

        return cls(
            sequence_output=sequence_output,
            sequence_actual=sequence_actual,
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
        for extr in self.sequence_output:
            output_extr = extr.extract(data=output_extr)

        for extr in self.sequence_actual:
            actual_extr = extr.extract(data=actual_extr)
        print(f"output: ")
        print(output_extr)
        print("actual")
        print(actual_extr)
        return self.eval_extractor.extract(output=output_extr, actual=actual_extr)

    def build(self, data):
        pass  # Do not support building for now. KISS

    def is_built(self):
        # sequences built?
        out_seq = all(extr.is_bult() for extr in self.sequence_output)
        act_seq = all(extr.is_bult() for extr in self.sequence_actual)
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
