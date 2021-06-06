import base64

import numpy as np

from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_distances, euclidean_distances

from raymon.profiling.extractors import SimpleExtractor


class KMeansOutlierScorer(SimpleExtractor):

    dist_choices = {"euclidean": euclidean_distances, "cosine": cosine_distances}

    def __init__(self, k=16, clusters=None, dist="euclidean"):
        self._k = None
        self._clusters = None
        self._dist = None
        self.k = k
        self.clusters = clusters
        self.dist = dist

    """
    PROPERTIES
    """

    @property
    def k(self):
        return self._k

    @k.setter
    def k(self, value):
        if isinstance(value, int) and value > 0:
            self._k = value
        else:
            raise ValueError(f"k must be an int > 0, not {value} ({type(value)})")

    @property
    def clusters(self):
        return self._clusters

    @clusters.setter
    def clusters(self, value):
        if value is None:
            self._clusters = None
            return
        nclusters, dim = value.shape
        value = value.astype(np.float64)
        if isinstance(value, np.ndarray) and nclusters == self._k:
            self._clusters = value
        else:
            raise ValueError(
                f"clusters must be an np.ndarray of shape ({self.k}, dim), not {type(value)} ({value.shape})"
            )

    @property
    def dist(self):
        if self._dist in self.dist_choices:
            return self.dist_choices[self._dist]
        else:
            raise ValueError(f"Invalid distance specified: {self._dist}")

    @dist.setter
    def dist(self, value):
        if isinstance(value, str) and value in self.dist_choices:
            self._dist = value
        else:
            raise ValueError(f"dist must be str and one of {self.dist_choices.keys()}, not {value}, ({type(value)})")

    @property
    def dim(self):
        return self.clusters.shape[1]

    def extract(self, data):
        def sum_2closest(distances):
            return np.sort(distances, axis=1)[:, :2].sum(axis=1)

        if data.shape == (self.dim,):
            data = data[None, :]
        elif data.shape == (1, self.dim):
            pass
        else:
            raise ValueError(f"data must be of shape {(1, self.dim)} or {(self.dim, )}, not {data.shape}")
        pairwise_dist = self.dist(data, self.clusters)
        return float(sum_2closest(pairwise_dist))

    """Buildable interface"""

    def build(self, data):
        data = np.array(data).astype(np.float64)
        km = KMeans(n_clusters=self.k)
        km.fit(data)
        clusters = km.cluster_centers_
        self.clusters = clusters

    def is_built(self):
        return self.clusters is not None and len(self.clusters) == self.k

    """Serializable interface"""

    def to_jcr(self):
        b64 = base64.b64encode(self.clusters).decode()
        shape = self.clusters.shape
        diststr = [k for k, v in self.dist_choices.items() if v == self.dist][0]
        data = {"clusters": b64, "k": self.k, "dist": diststr}

        state = {"class": self.class2str(), "state": data}
        return state

    @classmethod
    def from_jcr(cls, jcr):
        k = jcr["k"]
        b64 = jcr["clusters"]
        dist = jcr["dist"]
        clusters = np.frombuffer(base64.decodebytes(b64.encode()), dtype=np.float64).reshape((k, -1))
        return cls(k=k, clusters=clusters, dist=dist)
