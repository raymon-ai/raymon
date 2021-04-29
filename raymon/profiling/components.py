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
)
from raymon.profiling.stats import CategoricStats, NumericStats, equalize_domains
from raymon.tags import Tag, PROFILE_ERROR, PROFILE_FEATURE

HIST_N_SAMPLES = 1000


class Component(Serializable, Buildable, ABC):
    def __init__(self, name="default_name", extractor=None, importance=None):
        self._name = None
        self._importance = None
        self.name = name
        self.importance = importance
        self.extractor = extractor
        self.stats = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError(f"Component name should be a string")
        self._name = value.lower()

    @property
    def importance(self):
        return self._importance

    @importance.setter
    def importance(self, value):
        if isinstance(value, numbers.Number):
            self._importance = value
        elif value is None:
            self._importance = 0
        else:
            raise ValueError(f"feature importance for {self.name} must be a dict[str, Number]")

    """Serializable interface """

    def to_jcr(self):
        data = {
            "feature_class": self.class2str(),
            "feature": {
                "name": self.name,
                "extractor_class": self.extractor.class2str(),
                "extractor_state": self.extractor.to_jcr(),
                "importance": self.importance,
                "stats": self.stats.to_jcr(),
            },
        }
        return data

    @classmethod
    def from_jcr(cls, jcr):
        classpath = jcr["feature_class"]
        comp_jcr = jcr["feature"]
        compclass = locate(classpath)
        if compclass is None:
            raise NameError(f"Could not locate classpath {compclass}")
        feature = compclass.from_jcr(comp_jcr)
        return feature

    def build_extractor(self, input, output, actual):
        self.extractor.build(input, output, actual)

    def build_stats(self, input, output, actual):
        print(f"Compiling stats for {self.name}")
        features = self.extractor.extract_multiple(input, output, actual)
        self.stats.build(features)

    def build(self, input, output, actual):
        # Compile extractor
        self.build_extractor(input, output, actual)
        # Configure stats
        self.build_stats(input, output, actual)

    def is_built(self):
        return self.extractor.is_built() and self.stats.is_built()

    def validate(self, input, output, actual):
        feature = self.extractor.extract(input, output, actual)
        # Make a tag from the feature
        feat_tag = self.feature2tag(feature)
        # Check min, max, nan or None and raise data error
        err_tag = self.check_invalid(feature)
        tags = [feat_tag, err_tag]
        # Filter Nones
        tags = [tag for tag in tags if tag is not None]
        return tags

    @abstractmethod
    def feature2tag(self, feature):
        pass

    @abstractmethod
    def check_invalid(self, feature):
        pass

    def __repr__(self):
        return str(self)


class FloatComponent(Component):
    def __init__(self, name="default_name", extractor=None, importance=None, stats=None):
        super().__init__(name=name, extractor=extractor, importance=importance)
        self._stats = None
        self.stats = stats

    """
    PROPERTIES
    """

    @property
    def stats(self):
        return self._stats

    @stats.setter
    def stats(self, value):
        if value is None:
            self._stats = NumericStats()
        elif isinstance(value, NumericStats):
            self._stats = value
        else:
            raise DataException(f"stats for a NumericComponant should be of type NumericStats, not {type(value)}")

    def feature2tag(self, feature):
        if not np.isnan(feature):
            return Tag(name=self.name, value=float(feature), type=PROFILE_FEATURE)
        else:
            return None

    def check_invalid(self, feature):
        tagname = f"{self.name}-error"
        if feature is None:
            return Tag(name=tagname, value="Value None", type=PROFILE_ERROR)
        elif np.isnan(feature):
            return Tag(name=tagname, value="Value NaN", type=PROFILE_ERROR)
        elif feature > self.stats.max:
            return Tag(name=tagname, value="Value > max", type=PROFILE_ERROR)
        elif feature < self.stats.min:
            return Tag(name=tagname, value="Value < min", type=PROFILE_ERROR)
        else:
            return None

    @classmethod
    def from_jcr(cls, jcr):
        classpath = jcr["extractor_class"]
        extr_class = locate(classpath)
        if extr_class is None:
            NameError(f"Could not locate {classpath}")

        extractor = extr_class.from_jcr(jcr["extractor_state"])
        stats = NumericStats.from_jcr(jcr["stats"])
        importance = jcr["importance"]
        name = jcr["name"]
        return cls(name=name, extractor=extractor, importance=importance, stats=stats)

    def __str__(self):
        return f"FloatComponent(name={self.name}, extractor={self.extractor})"


class IntComponent(Component):
    def __init__(self, name="default_name", extractor=None, importance=None, stats=None):
        super().__init__(name=name, extractor=extractor, importance=importance)
        self._stats = None
        self.stats = stats

    """
    PROPERTIES
    """

    @property
    def stats(self):
        return self._stats

    @stats.setter
    def stats(self, value):
        if value is None:
            self._stats = NumericStats()
        elif isinstance(value, NumericStats):
            self._stats = value
        else:
            raise DataException(f"stats for a NumericComponant should be of type NumericStats, not {type(value)}")

    def feature2tag(self, feature):
        if not np.isnan(feature):
            return Tag(name=self.name, value=float(feature), type=PROFILE_FEATURE)
        else:
            return None

    def check_invalid(self, feature):
        tagname = f"{self.name}-error"
        if feature is None:
            return Tag(name=tagname, value="Value None", type=PROFILE_ERROR)
        elif np.isnan(feature):
            return Tag(name=tagname, value="Value NaN", type=PROFILE_ERROR)
        elif feature > self.stats.max:
            return Tag(name=tagname, value="Value > max", type=PROFILE_ERROR)
        elif feature < self.stats.min:
            return Tag(name=tagname, value="Value < min", type=PROFILE_ERROR)
        else:
            return None

    @classmethod
    def from_jcr(cls, jcr):
        classpath = jcr["extractor_class"]
        extr_class = locate(classpath)
        if extr_class is None:
            NameError(f"Could not locate {classpath}")

        extractor = extr_class.from_jcr(jcr["extractor_state"])
        stats = NumericStats.from_jcr(jcr["stats"])
        importance = jcr["importance"]

        name = jcr["name"]
        importance = jcr["importance"]
        return cls(name=name, extractor=extractor, importance=importance, stats=stats)

    def __str__(self):
        return f"IntComponent(name={self.name}, extractor={self.extractor})"


class CategoricComponent(Component):

    # Domain, domain distribution
    def __init__(self, name="default_name", extractor=None, importance=None, stats=None):
        super().__init__(name=name, extractor=extractor, importance=importance)
        self._stats = None
        self.stats = stats

    """
    PROPERTIES
    """

    @property
    def stats(self):
        return self._stats

    @stats.setter
    def stats(self, value):
        if value is None:
            self._stats = CategoricStats()
        elif isinstance(value, CategoricStats):
            self._stats = value
        else:
            raise DataException(f"stats for a NumericComponant should be of type CategoricStats, not {type(value)}")

    def feature2tag(self, feature):
        if isinstance(feature, str) or not np.isnan(feature):
            return Tag(name=self.name, value=feature, type=PROFILE_FEATURE)
        else:
            return None

    def check_invalid(self, feature):
        tagname = f"{self.name}-err"
        if feature is None:
            return Tag(name=tagname, value="Value None", type=PROFILE_ERROR)
        elif pd.isnull(feature):
            return Tag(name=tagname, value="Value NaN", type=PROFILE_ERROR)
        elif feature not in self.stats.frequencies:
            return Tag(name=tagname, value="Domain Error", type=PROFILE_ERROR)
        else:
            return None

    @classmethod
    def from_jcr(cls, jcr):
        classpath = jcr["extractor_class"]
        extr_class = locate(classpath)
        if extr_class is None:
            NameError(f"Could not locate {classpath}")

        extractor = extr_class.from_jcr(jcr["extractor_state"])
        stats = CategoricStats.from_jcr(jcr["stats"])
        importance = jcr["importance"]
        name = jcr["name"]

        return cls(name=name, extractor=extractor, importance=importance, stats=stats)

    def __str__(self):
        return f"CategoricComponent(name={self.name}, extractor={self.extractor})"
