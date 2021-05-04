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
from raymon.tags import Tag, CGROUP_TAGTYPES
from raymon.profiling.extractors import SimpleExtractor, ScoringExtractor

HIST_N_SAMPLES = 1000


class Component(Serializable, Buildable, ABC):
    def __init__(self, name, extractor, importance=None):
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
            raise ValueError(f"Component importance for {self.name} must be a dict[str, Number]")

    """Serializable interface """

    def to_jcr(self):
        data = {
            "component_class": self.class2str(),
            "component": {
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
        classpath = jcr["component_class"]
        comp_jcr = jcr["component"]
        compclass = locate(classpath)
        if compclass is None:
            raise NameError(f"Could not locate classpath {classpath}")
        component = compclass.from_jcr(comp_jcr)
        return component

    def build_extractor(self, data):
        self.extractor.build(data)

    def build_stats(self, data, domain=None):
        if isinstance(self.extractor, SimpleExtractor):
            components = self.extractor.extract_multiple(data)
        elif isinstance(self.extractor, ScoringExtractor):
            output, actual = data
            components = self.extractor.extract_multiple(output=output, actual=actual)
        else:
            raise ProfileStateException(f"Unknown Extractor type for {self}: {type(self.extractor)}")
        self.stats.build(components, domain=domain)

    def build(self, data, domain=None):
        # Compile extractor
        self.build_extractor(data)
        # Configure stats
        self.build_stats(data, domain=domain)

    def is_built(self):
        return self.extractor.is_built() and self.stats.is_built()

    def validate(self, data, cgroup):
        if isinstance(self.extractor, SimpleExtractor):
            component = self.extractor.extract(data)
        elif isinstance(self.extractor, ScoringExtractor):
            output, actual = data
            component = self.extractor.extract(output=output, actual=actual)
        else:
            raise ProfileStateException(f"Unknown Extractor type 'type(self.extractor)' for component {self.name}")
        # Make a tag from the component
        feat_tag = self.component2tag(component, cgroup=cgroup)
        # Check min, max, nan or None and raise data error
        err_tag = self.check_invalid(component, cgroup=cgroup)
        tags = [feat_tag, err_tag]
        # Filter Nones
        tags = [tag for tag in tags if tag is not None]
        return tags

    @abstractmethod
    def component2tag(self, component, cgroup):
        pass

    @abstractmethod
    def check_invalid(self, component, cgroup):
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

    def component2tag(self, component, cgroup):
        if not np.isnan(component):
            return Tag(name=self.name, value=float(component), type=CGROUP_TAGTYPES[cgroup]["tagtype"])
        else:
            return None

    def check_invalid(self, component, cgroup):
        tagname = f"{self.name}-error"
        if component is None:
            return Tag(name=tagname, value="Value None", type=CGROUP_TAGTYPES[cgroup]["errortype"])
        elif np.isnan(component):
            return Tag(name=tagname, value="Value NaN", type=CGROUP_TAGTYPES[cgroup]["errortype"])
        elif component > self.stats.max:
            return Tag(name=tagname, value="UpperBoundError", type=CGROUP_TAGTYPES[cgroup]["errortype"])
        elif component < self.stats.min:
            return Tag(name=tagname, value="LowerBoundError", type=CGROUP_TAGTYPES[cgroup]["errortype"])
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

    def component2tag(self, component, cgroup):
        if not np.isnan(component):
            return Tag(name=self.name, value=int(component), type=CGROUP_TAGTYPES[cgroup]["tagtype"])
        else:
            return None

    def check_invalid(self, component, cgroup):
        tagname = f"{self.name}-error"
        if component is None:
            return Tag(name=tagname, value="Value None", type=CGROUP_TAGTYPES[cgroup]["errortype"])
        elif np.isnan(component):
            return Tag(name=tagname, value="Value NaN", type=CGROUP_TAGTYPES[cgroup]["errortype"])
        elif component > self.stats.max:
            return Tag(name=tagname, value="UpperBoundError", type=CGROUP_TAGTYPES[cgroup]["errortype"])
        elif component < self.stats.min:
            return Tag(name=tagname, value="LowerBoundError", type=CGROUP_TAGTYPES[cgroup]["errortype"])
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

    def component2tag(self, component, cgroup):
        if isinstance(component, str) or not np.isnan(component):
            return Tag(name=self.name, value=component, type=CGROUP_TAGTYPES[cgroup]["tagtype"])
        else:
            return None

    def check_invalid(self, component, cgroup):
        tagname = f"{self.name}-err"
        if component is None:
            return Tag(name=tagname, value="Value None", type=CGROUP_TAGTYPES[cgroup]["errortype"])
        elif pd.isnull(component):
            return Tag(name=tagname, value="Value NaN", type=CGROUP_TAGTYPES[cgroup]["errortype"])
        elif component not in self.stats.frequencies:
            return Tag(name=tagname, value="Domain Error", type=CGROUP_TAGTYPES[cgroup]["errortype"])
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
