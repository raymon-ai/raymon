import numpy as np
import pandas as pd
import math
from abc import ABC, abstractmethod
from scipy.interpolate import interp1d
from pydoc import locate
from collections import defaultdict


from raymon.globals import (
    Buildable,
    Serializable,
    DataException,
)

from raymon.tags import Tag, CTYPE_TAGTYPES


class Stats(Serializable, Buildable, ABC):
    @abstractmethod
    def sample(self, n):
        raise NotImplementedError

    @abstractmethod
    def report_drift(self, other, threshold):
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

    _attrs = ["min", "max", "mean", "std", "invalids", "percentiles", "samplesize", "percentiles_lb", "percentiles_ub"]

    def __init__(
        self, min=None, max=None, mean=None, std=None, invalids=None, percentiles=None, samplesize=None, **kwargs
    ):
        self.samplesize = samplesize
        self.min = min
        self.max = max
        self.mean = mean
        self.std = std
        self.invalids = invalids

        self.percentiles = percentiles

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

        if self.samplesize and self.percentiles:
            lower, upper = self.conf_bounds_approx()
            self._percentiles_lb = lower
            self._percentiles_ub = upper
        else:
            self._percentiles_lb = None
            self._percentiles_ub = None

    @property
    def percentiles_lb(self):
        return self._percentiles_lb

    @property
    def percentiles_ub(self):
        return self._percentiles_ub

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

    def conf_bounds_approx(self):
        """
        The approximate method is about 9x times faster (2ms vs 18 ms on a simple timeit test)
        Get the confidence interval that encompasses the true CDF with 1-alpha certainty based on the DKW (Dvoretzky–Kiefer–Wolfowitz) inequality.
        References:
        - https://www.wikiwand.com/en/Dvoretzky%E2%80%93Kiefer%E2%80%93Wolfowitz_inequality
        - https://www.wikiwand.com/en/Empirical_distribution_function#/Confidence%20intervals


        Parameters
        ----------
        edf : np.array
            the empirical distribution function
        nobs : int
            number of observations used for the edf
        alpha : float, optional
            alpha as in the EKW, by default 0.05

        Returns
        -------
        list
            lower bounds
        list
            upper bound
        float
            epsilon, as in the DKW
        """
        #
        ys = list(range(101))
        alpha = 0.05
        epsilon = np.sqrt(np.log(2.0 / alpha) / (2 * self.samplesize)) * 100
        lower = np.clip(ys - epsilon, 0, 100)
        upper = np.clip(ys + epsilon, 0, 100)
        # now, get the x values that match the upper and lower y values so at the percentile points range(101)
        interpolator_lower = interp1d(
            x=lower, y=self.percentiles, fill_value=(self.percentiles[0], self.percentiles[-1]), bounds_error=False
        )
        perc_lb = interpolator_lower(list(range(101)))
        interpolator_upper = interp1d(
            x=upper, y=self.percentiles, fill_value=(self.percentiles[0], self.percentiles[-1]), bounds_error=False
        )
        perc_ub = interpolator_upper(list(range(101)))
        return perc_lb.tolist(), perc_ub.tolist()

    def conf_bounds_bootstrap(self, n=100):
        run_diffs = []
        q = np.arange(start=0, stop=101, step=1)
        original_perc = np.array(self.percentiles)
        for _ in range(100):
            px = self.sample(n=self.samplesize)
            percentiles = [float(a) for a in np.percentile(a=px, q=q, interpolation="higher")]
            perc_change = percentiles - original_perc
            run_diffs.append(perc_change)

        run_diffs = np.array(run_diffs)
        # sort columns
        lower_idx = int(n * 0.05)
        upper_idx = int(n * 0.95)
        runs, ps = run_diffs.shape
        for p in range(ps):
            run_diffs[:, p] = np.sort(run_diffs[:, p])
        percentile_lb = original_perc + run_diffs[lower_idx, :]
        percentile_ub = original_perc + run_diffs[upper_idx, :]
        return percentile_lb.tolist(), percentile_ub.tolist()

    def report_drift(self, other, threshold):
        if other.samplesize == 0:
            return {"drift": -1, "drift_idx": -1, "alert": False, "valid": False}

        merged_domain = np.sort(np.concatenate([self.percentiles, other.percentiles]))
        # If certain values cause jumps of multiple percentages, that value should be associated with the maximum percentage
        lb_self_interpolated = interpolate(self.percentiles_lb, merged_domain)
        lb_other_interpolated = interpolate(other.percentiles_lb, merged_domain)
        ub_self_interpolated = interpolate(self.percentiles_ub, merged_domain)
        ub_other_interpolated = interpolate(other.percentiles_ub, merged_domain)

        # Check one above other, and the reverse
        dists1 = np.array(lb_self_interpolated) - np.array(ub_other_interpolated)
        dists2 = np.array(lb_other_interpolated) - np.array(ub_self_interpolated)
        # Keep the maximum distance per x value, and only keep positive ones
        maxes = np.maximum(np.maximum(dists1, dists2), 0)
        drift = min(np.max(maxes), 100) / 100
        drift_xvalue = merged_domain[int(np.argmax(maxes))]
        # drift_xvalue = merged_domain[drift_idx]

        drift_report = {
            "drift": float(drift),
            "drift_xvalue": drift_xvalue,
            "alert": bool(drift > threshold),
            "valid": True,
        }
        return drift_report

    def sample(self, n, dtype="float"):
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
        if not math.isnan(value):
            return Tag(name=name, value=int(value), type=tagtype)
        else:
            return None

    def check_invalid(self, name, value, tagtype):
        tagname = f"{name}-error"
        if value is None:
            return Tag(name=tagname, value="Value None", type=tagtype)
        elif math.isnan(value):
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
        if not math.isnan(value):
            return Tag(name=name, value=float(value), type=tagtype)
        else:
            return None

    def check_invalid(self, name, value, tagtype):
        tagname = f"{name}-error"
        if value is None:
            return Tag(name=tagname, value="Value None", type=tagtype)
        elif math.isnan(value):
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

    _attrs = ["frequencies", "invalids", "samplesize", "frequencies_lb", "frequencies_ub"]

    def __init__(self, frequencies=None, invalids=None, samplesize=None, **kwargs):

        self.samplesize = samplesize
        self.frequencies = frequencies
        self.invalids = invalids

    """frequencies"""

    @property
    def frequencies(self):
        return self._frequencies

    @frequencies.setter
    def frequencies(self, value):
        if value is None:
            self._frequencies = None

        elif isinstance(value, dict):
            for key, keyvalue in value.items():
                if keyvalue < 0:
                    raise DataException(f"Domain count for {key} is  < 0")
            self._frequencies = value
        else:
            raise DataException(f"stats.frequencies should be a dict, not {type(value)}")

        if self.samplesize and self.frequencies:
            lower, upper = self.conf_bounds_approx()
            self._frequencies_lb = lower
            self._frequencies_ub = upper
        else:
            self._frequencies_lb = None
            self._frequencies_ub = None

    @property
    def frequencies_lb(self):
        return self._frequencies_lb

    @property
    def frequencies_ub(self):
        return self._frequencies_ub

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

    def f(self, key):
        if key in self.frequencies:
            return self.frequencies[key]
        else:
            return 0

    def f_lb(self, key):
        if key in self.frequencies_lb:
            return self.frequencies_lb[key]
        else:
            return 0

    def f_ub(self, key):
        if key in self.frequencies_ub:
            return self.frequencies_ub[key]
        else:
            return 0

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

    def conf_bounds_approx(self):
        """
        The approximated CI is about 25x faster. (4ms vs 100ms on a simple timeit test)
        Estimate the 95% confidence interval for the distributions, using the "Normal Approximation Method" of the Binomial Confidence Interval.
        References:
        - https://stats.stackexchange.com/questions/111355/confidence-interval-and-sample-size-multinomial-probabilities
        - https://www.dummies.com/education/science/biology/the-confidence-interval-around-an-event-count-or-rate/
        Parameters
        ----------
        frequencies : [type]
            [description]
        nobs : [type]
            [description]
        """
        lower = {}
        upper = {}
        z = 1.96  # z score of 1.96 leads to 95% interval (gaussian)
        for key, prob in self.frequencies.items():
            std_dev = math.sqrt(prob * (1 - prob) / self.samplesize)
            error = z * std_dev
            upper[key] = min(prob + error, 1)
            lower[key] = max(prob - error, 0)
        return lower, upper

    def conf_bounds_bootstrap(self, n=100):

        run_diffs = defaultdict(list)
        lower_idx = int(n * 0.95)
        upper_idx = int(n * 0.05)

        for _ in range(n):
            s = self.sample(n=self.samplesize)
            frequencies_sampled = pd.Series(s).value_counts(normalize=True).to_dict()
            for key in self.frequencies.keys():
                run_diffs[key].append(frequencies_sampled.get(key, 0) - self.frequencies[key])

        freq_lb = {}
        freq_ub = {}
        for key in run_diffs:
            errors_sorted = np.sort(run_diffs[key])
            freq_lb[key] = max(0, self.frequencies[key] - errors_sorted[upper_idx])
            freq_ub[key] = min(1, self.frequencies[key] - errors_sorted[lower_idx])

        return freq_lb, freq_ub

    def report_drift(self, other, threshold):
        if other.samplesize == 0:
            return {"drift": -1, "drift_idx": -1, "alert": False, "valid": False}
        _, _, full_domain = equalize_domains(self.frequencies, other.frequencies)

        # The following boils down to the Chebyshev distance between the confidence intervals
        max_diff = -1
        max_diff_idx = 0
        for k in full_domain:
            diff = max([self.f_lb(k) - other.f_ub(k), other.f_lb(k) - self.f_ub(k), 0])
            if diff > max_diff:
                max_diff = diff
                max_diff_idx = k

        drift = min(max_diff, 1)
        drift_idx = max_diff_idx
        drift_report = {"drift": float(drift), "drift_idx": drift_idx, "alert": bool(drift > threshold), "valid": True}

        return drift_report

    def sample(self, n):
        domain = sorted(list(self.frequencies.keys()))
        # Let's be absolutely sure the domain is always in the same order
        p = [self.frequencies[k] for k in domain]
        return np.random.choice(a=domain, size=n, p=p)

    def sample_counts(self, domain_freq, keys, n):
        domain = sorted(list(keys))
        # Le's be absolutely sure the domain is always in the same order
        p = [domain_freq.get(k, 0) for k in domain]
        counts = (np.array(p) * (n - len(domain))).astype("int")
        counts += 1  # make sure there are no zeros
        return counts

    def component2tag(self, name, value, tagtype):
        if isinstance(value, str):
            return Tag(name=name, value=str(value), type=tagtype)
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


def interpolate(percentiles, merged_domain):
    # If certain values cause jumps of multiple percentages, that value should be associated with the maximum percentage
    cdf = np.searchsorted(percentiles, percentiles, side="right")
    # cdf contains the y points
    interpolator = interp1d(x=percentiles, y=cdf, fill_value=(0, 100), bounds_error=False)
    cdf_interpolated = interpolator(merged_domain)
    return cdf_interpolated
