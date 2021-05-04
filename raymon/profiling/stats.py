import numpy as np
import pandas as pd

from abc import ABC, abstractmethod
from scipy.interpolate import interp1d

from scipy.stats import ks_2samp

from raymon.globals import (
    Buildable,
    Serializable,
    DataException,
)

N_SAMPLES = 500


class Stats(Serializable, Buildable, ABC):
    @abstractmethod
    def sample(self, n):
        raise NotImplementedError

    @abstractmethod
    def contrast(self, other):
        raise NotImplementedError


class NumericStats(Stats):

    _attrs = ["min", "max", "mean", "std", "pinv", "percentiles", "samplesize"]

    def __init__(self, min=None, max=None, mean=None, std=None, pinv=None, percentiles=None, samplesize=None):

        self.min = min
        self.max = max
        self.mean = mean
        self.std = std
        self.pinv = pinv
        self.percentiles = percentiles
        self.samplesize = samplesize

    """MIN"""

    @property
    def min(self):
        return self._min

    @min.setter
    def min(self, value):
        if value is np.nan:
            raise DataException("stats.min cannot be NaN")
        self._min = value

    """MAX"""

    @property
    def max(self):
        return self._max

    @max.setter
    def max(self, value):
        if value is np.nan:
            raise DataException("stats.max cannot be NaN")
        self._max = value

    """MEAN"""

    @property
    def mean(self):
        return self._mean

    @mean.setter
    def mean(self, value):
        if value is np.nan:
            raise DataException("stats.mean cannot be NaN")
        self._mean = value

    """STD"""

    @property
    def std(self):
        return self._std

    @std.setter
    def std(self, value):
        if value is np.nan:
            raise DataException("stats.std cannot be NaN")
        self._std = value

    """PINV"""

    @property
    def pinv(self):
        return self._pinv

    @pinv.setter
    def pinv(self, value):
        if value is np.nan:
            raise DataException("stats.pinv cannot be NaN")
        self._pinv = value

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
        if value is np.nan:
            raise DataException("stats.samplesize cannot be NaN")
        self._samplesize = value

    """Serializable Interface"""

    def to_jcr(self):
        data = {}
        for attr in self._attrs:
            data[attr] = getattr(self, attr)
        return data

    @classmethod
    def from_jcr(cls, jcr):
        d = {}
        for attr in cls._attrs:
            d[attr] = jcr.get(attr, None)
        return cls(**d)

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
        self.pinv = (n_invalids + n_nans) / self.samplesize

    def is_built(self):
        return all(getattr(self, attr) is not None for attr in self._attrs)

    """Testing and sampling functions"""

    def contrast(self, other):
        # KS distance
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
        drift = np.max(np.abs(interpolated_1 - interpolated_2)) / 100
        drift_idx = int(np.argmax(np.abs(interpolated_1 - interpolated_2)))
        # alert_drift = drift > thresh_drift

        pinv1 = self.pinv
        pinv2 = other.pinv
        pinvdiff = pinv2 - pinv1
        # alert_inv = pinvdiff > thresh_inv

        return drift, drift_idx, pinvdiff

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


class CategoricStats(Stats):

    _attrs = ["frequencies", "pinv", "samplesize"]

    def __init__(self, frequencies=None, pinv=None, samplesize=None):

        self.frequencies = frequencies
        self.pinv = pinv
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
    def pinv(self):
        return self._pinv

    @pinv.setter
    def pinv(self, value):
        if value is np.nan:
            raise DataException("stats.pinv cannot be NaN")
        self._pinv = value

    @property
    def samplesize(self):
        return self._samplesize

    @samplesize.setter
    def samplesize(self, value):
        if value is np.nan:
            raise DataException("stats.samplesize cannot be NaN")
        self._samplesize = value

    def to_jcr(self):
        data = {}
        for attr in self._attrs:
            value = getattr(self, attr)
            data[attr] = value
        return data

    @classmethod
    def from_jcr(cls, jcr):
        d = {}
        for attr in cls._attrs:
            d[attr] = jcr.get(attr, None)
        return cls(**d)

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
        self.pinv = (n_nans + n_invalids) / self.samplesize

    def is_built(self):
        return all(getattr(self, attr) is not None for attr in self._attrs)

    """Testing and sampling functions"""

    def contrast(self, other):
        self_f, other_f, full_domain = equalize_domains(self.frequencies, other.frequencies)
        f_sorted_self = []
        f_sorted_other = []
        for k in full_domain:
            f_sorted_self.append(self_f[k])
            f_sorted_other.append(other_f[k])
        f_sorted_self = np.array(f_sorted_self)
        f_sorted_other = np.array(f_sorted_other)
        # Chebyshev
        drift = np.max(np.abs(f_sorted_self - f_sorted_other))
        drift_idx = full_domain[np.argmax(np.abs(f_sorted_self - f_sorted_other))]
        # alert_drift = drift > thresh_drift

        pinv1 = self.pinv
        pinv2 = other.pinv
        pinvdiff = pinv2 - pinv1
        # alert_inv = pinvdiff > thresh_inv

        return drift, drift_idx, pinvdiff

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
