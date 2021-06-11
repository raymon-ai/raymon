import numpy as np
import pandas as pd
import math
from abc import ABC, abstractmethod
from scipy.interpolate import interp1d
from pydoc import locate


from raymon.globals import (
    Buildable,
    Serializable,
    DataException,
)

N_SAMPLES = 500
from raymon.tags import Tag, CTYPE_TAGTYPES


class Stats(Serializable, Buildable, ABC):
    @abstractmethod
    def sample(self, n):
        raise NotImplementedError

    @abstractmethod
    def report_drift(self, other, threshold):
        raise NotImplementedError

    @abstractmethod
    def report_mean_diff(self, other, threshold, use_abs=False):
        raise NotImplementedError

    def report_invalid_diff(self, other, threshold):
        if other.samplesize == 0:
            return {"invalids": "_", "alert": False, "valid": False}
        invalidsdiff = other.invalids - self.invalids
        invalids_report = {
            "invalids": float(invalidsdiff),
            "alert": bool(invalidsdiff > threshold),
            "valid": True,
        }
        return invalids_report

    @abstractmethod
    def component2tag(self, component, tagtype):
        pass

    @abstractmethod
    def check_invalid(self, component, tagtype):
        pass

    def to_jcr(self):
        state = {}
        for attr in self._attrs:
            state[attr] = getattr(self, attr)
        data = {"class": self.class2str(), "state": state}
        return data

    @classmethod
    def from_jcr(cls, jcr):
        classpath = jcr["class"]
        state_jcr = jcr["state"]
        statsclass = locate(classpath)
        if statsclass is None:
            raise NameError(f"Could not locate classpath {classpath}")
        return statsclass.from_jcr(state_jcr)


class NumericStats(Stats):

    _attrs = ["min", "max", "mean", "std", "invalids", "percentiles", "samplesize"]

    def __init__(self, min=None, max=None, mean=None, std=None, invalids=None, percentiles=None, samplesize=None):

        self.min = min
        self.max = max
        self.mean = mean
        self.std = std
        self.invalids = invalids
        self.percentiles = percentiles
        self.samplesize = samplesize

    """MIN"""

    @property
    def min(self):
        return self._min

    @min.setter
    def min(self, value):
        if value is not None and math.isnan(value):
            raise DataException("stats.min cannot be NaN")
        self._min = value

    """MAX"""

    @property
    def max(self):
        return self._max

    @max.setter
    def max(self, value):
        if value is not None and math.isnan(value):
            raise DataException("stats.max cannot be NaN")
        self._max = value

    """MEAN"""

    @property
    def mean(self):
        return self._mean

    @mean.setter
    def mean(self, value):
        if value is not None and math.isnan(value):
            raise DataException("stats.mean cannot be NaN")
        self._mean = value

    """STD"""

    @property
    def std(self):
        return self._std

    @std.setter
    def std(self, value):
        if value is not None and math.isnan(value):
            raise DataException("stats.std cannot be NaN")
        self._std = value

    """PINV"""

    @property
    def invalids(self):
        return self._invalids

    @invalids.setter
    def invalids(self, value):
        if value is not None and math.isnan(value):
            raise DataException("stats.invalids cannot be NaN")
        self._invalids = value

    """Percentiles"""

    @property
    def percentiles(self):
        return self._percentiles

    @percentiles.setter
    def percentiles(self, value):
        if value is None:
            self._percentiles = None
        elif len(value) == 101:
            self._percentiles = list(value)
        else:
            raise DataException("stats.percentiles must be None or a list of length 101.")

    """Size of the sample that was analyzed"""

    @property
    def samplesize(self):
        return self._samplesize

    @samplesize.setter
    def samplesize(self, value):
        if value is not None and math.isnan(value):
            raise DataException("stats.samplesize cannot be NaN")
        self._samplesize = value

    @property
    def range(self):
        return self.max - self.min

    """Buildable Interface"""

    def build(self, data, domain=None):
        """

        Parameters
        ----------
        data : [type]
            [description]
        domain : [type], optional
                    For numericstats, the domain is the range of values: (min, max). One or both can also be None. by default None
        """
        data = np.array(data)
        self.samplesize = len(data)
        nan = np.isnan(data)
        n_nans = len(data[nan])
        data = data[~nan]

        if domain and domain[0] is not None:
            self.min = domain[0]
        else:
            self.min = float(np.min(data))

        if domain and domain[1] is not None:
            self.max = domain[1]
        else:
            self.max = float(np.max(data))
        valid = (self.min <= data) & (self.max >= data)
        n_invalids = len(data[~valid])
        data = data[valid]

        self.mean = float(data.mean())
        self.std = float(data.std())

        # Build cdf estimate based on percentiles
        q = np.arange(start=0, stop=101, step=1)
        self.percentiles = [float(a) for a in np.percentile(a=data, q=q, interpolation="higher")]

        # Check the invalid
        self.invalids = (n_invalids + n_nans) / self.samplesize

    def is_built(self):
        return all(getattr(self, attr) is not None for attr in self._attrs)

    """Testing and sampling functions"""

    def report_drift(self, other, threshold):
        if other.samplesize == 0:
            return {"drift": -1, "drift_idx": -1, "alert": False, "valid": False}
        p1 = self.percentiles
        p2 = other.percentiles
        data_all = np.concatenate([p1, p2])
        # interp = np.sort(data_all)
        # If certain values cause jumps of multiple percentiles, that value should be associated with the maximum percentile
        cdf1 = np.searchsorted(p1, p1, side="right")
        cdf2 = np.searchsorted(p2, p2, side="right")
        interpolator_1 = interp1d(x=p1, y=cdf1, fill_value=(0, 100), bounds_error=False)
        interpolator_2 = interp1d(x=p2, y=cdf2, fill_value=(0, 100), bounds_error=False)
        interpolated_1 = interpolator_1(data_all)
        interpolated_2 = interpolator_2(data_all)
        drift = min(np.max(np.abs(interpolated_1 - interpolated_2)), 100) / 100
        drift_idx = int(np.argmax(np.abs(interpolated_1 - interpolated_2)))

        drift_report = {"drift": float(drift), "drift_idx": drift_idx, "alert": bool(drift > threshold), "valid": True}
        return drift_report

    def report_mean_diff(self, other, threshold, use_abs):
        if other.samplesize == 0:
            return {"mean": -1, "alert": False, "valid": False}
        meandiff = other.mean - self.mean
        meandiff_perc = meandiff / self.mean
        if use_abs:
            alert = bool(abs(meandiff_perc) > abs(threshold))
        else:
            alert = bool(meandiff_perc > threshold)
        invalids_report = {
            "mean": float(meandiff_perc),
            "alert": alert,
            "valid": True,
        }
        return invalids_report

    def sample(self, n=N_SAMPLES, dtype="float"):
        # Sample floats in range 0 - len(percentiles)
        samples = np.random.random(n) * 100

        # We will lineraly interpolate the sample between the percentiles, so get their integer floor and ceil percentile, and the relative diztance from the floor (between 0 and 1)
        floor_percentiles = np.floor(samples).astype("uint8")
        ceil_percentiles = np.ceil(samples).astype("uint8")
        percentiles_alpha = samples - np.floor(samples)

        percentiles = np.array(self.percentiles)
        px = percentiles[floor_percentiles] * (1 - percentiles_alpha) + percentiles[ceil_percentiles] * (
            percentiles_alpha
        )

        if dtype == "int":
            return px.astype(np.int)
        else:
            return px


class IntStats(NumericStats):
    def component2tag(self, name, value, tagtype):
        if not np.isnan(value):
            return Tag(name=name, value=int(value), type=tagtype)
        else:
            return None

    def check_invalid(self, name, value, tagtype):
        tagname = f"{name}-error"
        if value is None:
            return Tag(name=tagname, value="Value None", type=tagtype)
        elif np.isnan(value):
            return Tag(name=tagname, value="Value NaN", type=tagtype)
        elif value > self.max:
            return Tag(name=tagname, value="UpperBoundError", type=tagtype)
        elif value < self.min:
            return Tag(name=tagname, value="LowerBoundError", type=tagtype)
        else:
            return None

    @classmethod
    def from_jcr(cls, data):
        return cls(**data)


class FloatStats(NumericStats):
    def component2tag(self, name, value, tagtype):
        if not np.isnan(value):
            return Tag(name=name, value=float(value), type=tagtype)
        else:
            return None

    def check_invalid(self, name, value, tagtype):
        tagname = f"{name}-error"
        if value is None:
            return Tag(name=tagname, value="Value None", type=tagtype)
        elif np.isnan(value):
            return Tag(name=tagname, value="Value NaN", type=tagtype)
        elif value > self.max:
            return Tag(name=tagname, value="UpperBoundError", type=tagtype)
        elif value < self.min:
            return Tag(name=tagname, value="LowerBoundError", type=tagtype)
        else:
            return None

    @classmethod
    def from_jcr(cls, data):
        return cls(**data)


class CategoricStats(Stats):

    _attrs = ["frequencies", "invalids", "samplesize"]

    def __init__(self, frequencies=None, invalids=None, samplesize=None):

        self.frequencies = frequencies
        self.invalids = invalids
        self.samplesize = samplesize

    """frequencies"""

    @property
    def frequencies(self):
        return self._frequencies

    @frequencies.setter
    def frequencies(self, value):
        if value is None:
            self._frequencies = value
        elif isinstance(value, dict):
            for key, keyvalue in value.items():
                if keyvalue < 0:
                    raise DataException(f"Domain count for {key} is  < 0")
            self._frequencies = value
        else:
            raise DataException(f"stats.frequencies should be a dict, not {type(value)}")

    """PINV"""

    @property
    def invalids(self):
        return self._invalids

    @invalids.setter
    def invalids(self, value):
        if value is not None and math.isnan(value):
            raise DataException("stats.invalids cannot be NaN")
        self._invalids = value

    @property
    def samplesize(self):
        return self._samplesize

    @samplesize.setter
    def samplesize(self, value):
        if value is not None and math.isnan(value):
            raise DataException("stats.samplesize cannot be NaN")
        self._samplesize = value

    @property
    def range(self):
        return 1

    def build(self, data, domain=None):
        """[summary]

        Parameters
        ----------
        data : [type]
            [description]
        domain : [type], optional
            The domain of the featrue. A list or set, by default None
        """
        data = pd.Series(data)
        self.samplesize = len(data)
        nan = pd.isna(data)
        n_nans = len(data[nan])
        data = data[~nan]

        if domain:
            domain = set(domain)
            valid = data.isin(domain)
            n_invalids = len(data[~valid])
            data = data[valid]
        else:
            n_invalids = 0
        self.frequencies = data.value_counts(normalize=True).to_dict()
        self.invalids = (n_nans + n_invalids) / self.samplesize

    def is_built(self):
        return all(getattr(self, attr) is not None for attr in self._attrs)

    """Testing and sampling functions"""

    def report_drift(self, other, threshold):
        if other.samplesize == 0:
            return {"drift": -1, "drift_idx": -1, "alert": False, "valid": False}
        self_f, other_f, full_domain = equalize_domains(self.frequencies, other.frequencies)
        f_sorted_self = []
        f_sorted_other = []
        for k in full_domain:
            f_sorted_self.append(self_f[k])
            f_sorted_other.append(other_f[k])
        f_sorted_self = np.array(f_sorted_self)
        f_sorted_other = np.array(f_sorted_other)
        # Chebyshev
        drift = min(np.max(np.abs(f_sorted_self - f_sorted_other)), 100)
        drift_idx = full_domain[np.argmax(np.abs(f_sorted_self - f_sorted_other))]
        drift_report = {"drift": float(drift), "drift_idx": drift_idx, "alert": bool(drift > threshold), "valid": True}

        return drift_report

    def report_mean_diff(self, other, threshold, use_abs=False):
        return {"mean": -1, "alert": False, "valid": False}

    def sample(self, n):
        domain = sorted(list(self.frequencies.keys()))
        # Let's be absolutely sure the domain is always in the same order
        p = [self.frequencies[k] for k in domain]
        return np.random.choice(a=domain, size=n, p=p)

    def sample_counts(self, domain_freq, keys, n=N_SAMPLES):
        domain = sorted(list(keys))
        # Le's be absolutely sure the domain is always in the same order
        p = [domain_freq.get(k, 0) for k in domain]
        counts = (np.array(p) * (n - len(domain))).astype("int")
        counts += 1  # make sure there are no zeros
        return counts

    def component2tag(self, name, value, tagtype):
        if isinstance(value, str) or not np.isnan(value):
            return Tag(name=name, value=value, type=tagtype)
        else:
            return None

    def check_invalid(self, name, value, tagtype):
        tagname = f"{name}-error"
        if value is None:
            return Tag(name=tagname, value="Value None", type=tagtype)
        elif pd.isnull(value):
            return Tag(name=tagname, value="Value NaN", type=tagtype)
        elif value not in self.frequencies:
            return Tag(name=tagname, value="Domain Error", type=tagtype)
        else:
            return None

    @classmethod
    def from_jcr(cls, data):
        return cls(**data)


def add_missing(frequencies, full_domain):
    for key in full_domain:
        if key not in frequencies:
            frequencies[key] = 0
    return frequencies


def equalize_domains(a, b):
    full_domain = sorted(list(set(set(a.keys()) | set(b.keys()))))
    a = add_missing(a, full_domain)
    b = add_missing(b, full_domain)
    return a, b, full_domain
