from collections.abc import Iterable
from pydoc import locate
from abc import ABC, abstractmethod
import numbers
import numpy as np
import pandas as pd

from raymon.globals import (
    Buildable,
    Serializable,
    DataException,
    ProfileStateException,
    ComponentStateException,
)
from raymon.profiling.stats import Stats, CategoricStats, FloatStats, IntStats, equalize_domains
from raymon.tags import Tag, CTYPE_TAGTYPES
from raymon.profiling.extractors import Extractor, NoneExtractor, NoneEvalExtractor


class DataType:
    INT = "INT"
    FLOAT = "FLOAT"
    CAT = "CAT"


class Component(Serializable, Buildable, ABC):
    def __init__(self, name, extractor, dtype=DataType.FLOAT, stats=None):
        self.name = name
        self.extractor = extractor
        self.dtype = dtype
        self.stats = stats

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError(f"Component name should be a string")
        self._name = value.lower()

    @property
    def extractor(self):
        return self._extractor

    @extractor.setter
    def extractor(self, value):
        if not isinstance(value, Extractor):
            raise ValueError(f"Extractor should be a subclass of Extractor")
        self._extractor = value

    @property
    def dtype(self):
        return self._dtype

    @dtype.setter
    def dtype(self, value):
        if not value in [DataType.FLOAT, DataType.INT, DataType.CAT]:
            raise ValueError(f"Component dtype not valid.")
        self._dtype = value

    @property
    def stats(self):
        return self._stats

    @stats.setter
    def stats(self, value):
        if value is None:
            if self.dtype == DataType.FLOAT:
                self._stats = FloatStats()
            elif self.dtype == DataType.INT:
                self._stats = IntStats()
            else:
                self._stats = CategoricStats()

        elif isinstance(value, FloatStats) and self.dtype == DataType.FLOAT:
            self._stats = value
        elif isinstance(value, IntStats) and self.dtype == DataType.INT:
            self._stats = value
        elif isinstance(value, CategoricStats) and self.dtype == DataType.CAT:
            self._stats = value
        else:
            raise DataException(f"Stats type / dtype mismatch. {self.dtype} <-> {type(value)}")

    """Serializable interface """

    def to_jcr(self):

        data = {
            "class": self.class2str(),
            "state": {
                "name": self.name,
                "dtype": self.dtype,
                "stats": self.stats.to_jcr(),
                "extractor": self.extractor.to_jcr(),
            },
        }
        return data

    @classmethod
    def from_jcr(cls, jcr, mock_extractor=False):
        classpath = jcr["class"]
        compclass = locate(classpath)
        if compclass is None:
            raise NameError(f"Could not locate classpath {classpath}")
        return compclass.from_jcr(jcr["state"])

    def build_extractor(self, data):
        self.extractor.build(data)

    def build(self, data, domain=None):
        # Compile extractor
        self.build_extractor(data)
        # Configure stats
        return self.build_stats(data, domain=domain)

    def is_built(self):
        return self.extractor.is_built() and self.stats.is_built()

    def contrast(self, other, thresholds):

        invalids_threshold = thresholds.get("invalids", 0.01)
        drift_threshold = thresholds.get("drift", 0.05)
        try:
            if not self.is_built():
                print(f"Component {self.name} in 'self' is not built.")
                raise ComponentStateException(f"Component {self.name} in 'self' is not built.")
            if not other.is_built():
                print(f"Component {other.name} in 'other' is not built.")
                raise ComponentStateException(f"Component {other.name} in 'other' is not built.")
            drift_report = self.stats.report_drift(other.stats, threshold=drift_threshold)
            invalids_report = self.stats.report_invalid_diff(other.stats, threshold=invalids_threshold)

            return {"drift": drift_report, "invalids": invalids_report}
        except ComponentStateException as e:
            return {}

    def __repr__(self):
        return str(self)


class InputComponent(Component):
    def __init__(self, name, extractor, dtype=DataType.FLOAT, stats=None):
        super().__init__(name=name, extractor=extractor, dtype=dtype, stats=stats)

    def build_stats(self, data, domain=None):
        extracted = self.extractor.extract_multiple(data)
        self.stats.build(extracted, domain=domain)
        return extracted

    def validate(self, data):
        component = self.extractor.extract(data)
        # Make a tag from the component
        feat_tag = self.stats.component2tag(name=self.name, value=component, tagtype=CTYPE_TAGTYPES["input"]["tagtype"])
        # Check min, max, nan or None and raise data error
        err_tag = self.stats.check_invalid(
            name=self.name, value=component, tagtype=CTYPE_TAGTYPES["input"]["errortype"]
        )
        tags = [feat_tag, err_tag]
        # Filter Nones
        tags = [tag for tag in tags if tag is not None]
        return tags

    @classmethod
    def from_jcr(cls, jcr, mock_extractor=False):
        name = jcr["name"]
        dtype = jcr["dtype"]
        stats = Stats.from_jcr(jcr["stats"])
        if mock_extractor:
            extractor = NoneExtractor()
        else:
            extractor = Extractor.from_jcr(jcr["extractor"])
        component = cls(name=name, extractor=extractor, stats=stats, dtype=dtype)
        return component

    def __str__(self):
        return f"InputComponent(name={self.name}, dtype={self.dtype}, extractor={self.extractor})"


class OutputComponent(Component):
    def __init__(self, name, extractor, dtype=DataType.FLOAT, stats=None):
        super().__init__(name=name, extractor=extractor, dtype=dtype, stats=stats)

    def build_stats(self, data, domain=None):
        extracted = self.extractor.extract_multiple(data)
        self.stats.build(extracted, domain=domain)
        return extracted

    def validate(self, data):
        component = self.extractor.extract(data)
        # Make a tag from the component
        feat_tag = self.stats.component2tag(
            name=self.name, value=component, tagtype=CTYPE_TAGTYPES["output"]["tagtype"]
        )
        # Check min, max, nan or None and raise data error
        err_tag = self.stats.check_invalid(
            name=self.name, value=component, tagtype=CTYPE_TAGTYPES["output"]["errortype"]
        )
        tags = [feat_tag, err_tag]
        # Filter Nones
        tags = [tag for tag in tags if tag is not None]
        return tags

    @classmethod
    def from_jcr(cls, jcr, mock_extractor=False):
        name = jcr["name"]
        dtype = jcr["dtype"]
        stats = Stats.from_jcr(jcr["stats"])
        if mock_extractor:
            extractor = NoneExtractor()
        else:
            extractor = Extractor.from_jcr(jcr["extractor"])
        component = cls(name=name, extractor=extractor, stats=stats, dtype=dtype)
        return component

    def __str__(self):
        return f"OutputComponent(name={self.name}, dtype={self.dtype}, extractor={self.extractor})"


class ActualComponent(Component):
    def __init__(self, name, extractor, dtype=DataType.FLOAT, stats=None):
        super().__init__(name=name, extractor=extractor, dtype=dtype, stats=stats)

    def build_stats(self, data, domain=None):
        extracted = self.extractor.extract_multiple(data)
        self.stats.build(extracted, domain=domain)
        return extracted

    def validate(self, data):
        component = self.extractor.extract(data)
        # Make a tag from the component
        feat_tag = self.stats.component2tag(
            name=self.name, value=component, tagtype=CTYPE_TAGTYPES["actual"]["tagtype"]
        )
        # Check min, max, nan or None and raise data error
        err_tag = self.stats.check_invalid(
            name=self.name, value=component, tagtype=CTYPE_TAGTYPES["actual"]["errortype"]
        )
        tags = [feat_tag, err_tag]
        # Filter Nones
        tags = [tag for tag in tags if tag is not None]
        return tags

    @classmethod
    def from_jcr(cls, jcr, mock_extractor=False):
        name = jcr["name"]
        dtype = jcr["dtype"]
        stats = Stats.from_jcr(jcr["stats"])
        if mock_extractor:
            extractor = NoneExtractor()
        else:
            extractor = Extractor.from_jcr(jcr["extractor"])
        component = cls(name=name, extractor=extractor, stats=stats, dtype=dtype)
        return component

    def __str__(self):
        return f"ActualComponent(name={self.name}, dtype={self.dtype}, extractor={self.extractor})"


class EvalComponent(Component):
    def __init__(self, name, extractor, dtype=DataType.FLOAT, stats=None):
        super().__init__(name=name, extractor=extractor, dtype=dtype, stats=stats)

    def build_stats(self, data, domain=None):
        output, actual = data
        extracted = self.extractor.extract_multiple(output=output, actual=actual)
        self.stats.build(extracted, domain=domain)
        return extracted

    def validate(self, data):
        output, actual = data
        component = self.extractor.extract(output=output, actual=actual)
        # Make a tag from the component
        feat_tag = self.stats.component2tag(name=self.name, value=component, tagtype=CTYPE_TAGTYPES["eval"]["tagtype"])
        # Check min, max, nan or None and raise data error
        err_tag = self.stats.check_invalid(name=self.name, value=component, tagtype=CTYPE_TAGTYPES["eval"]["errortype"])
        tags = [feat_tag, err_tag]
        # Filter Nones
        tags = [tag for tag in tags if tag is not None]
        return tags

    @classmethod
    def from_jcr(cls, jcr, mock_extractor=False):
        name = jcr["name"]
        dtype = jcr["dtype"]
        stats = Stats.from_jcr(jcr["stats"])
        if mock_extractor:
            extractor = NoneEvalExtractor()
        else:
            extractor = Extractor.from_jcr(jcr["extractor"])
        component = cls(name=name, extractor=extractor, stats=stats, dtype=dtype)
        return component

    def __str__(self):
        return f"EvalComponent(name={self.name}, dtype={self.dtype}, extractor={self.extractor})"
