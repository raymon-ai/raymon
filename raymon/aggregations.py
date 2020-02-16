import numpy as np
from abc import abstractmethod
import raymon.types as rt


class Aggregation:

    @abstractmethod
    def __call__(self, data):
        pass


class HistogramAvg(Aggregation):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, hist_list):
        first_hist = hist_list[0]
        counts = np.zeros_like(first_hist.counts)
        for hist in hist_list:
            counts += hist.counts
        counts = counts / len(hist_list)
        hist = rt.Histogram(counts=counts, edges=first_hist.edges)
        return hist


aggs = {
    'HistogramAvg': HistogramAvg,
}
