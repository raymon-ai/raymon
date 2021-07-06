import base64
import json
import random
from pathlib import Path

import imagehash
import numpy as np
from raymon.profiling.extractors import SimpleExtractor


class FixedSubpatchSimilarity(SimpleExtractor):

    _attrs = ["patch", "refs"]
    _patch_keys = ["x0", "y0", "x1", "y1"]

    def __init__(self, patch, refs=None, nrefs=10, idfr=None):
        """[summary]

        Args:
            patch ([int], optional): [description]. The x0, y0, x1, y1 of the patch to look at.
            refs ([np.array], optional): [description]. References of what the patch should look like
        """
        self._nrefs = None
        self._patch = None
        self._refs = None
        self._idfr = None

        self.patch = patch
        self.nrefs = nrefs
        self.refs = refs
        self.idfr = idfr

    """
    PROPERTIES
    """

    @property
    def patch(self):
        return self._patch

    @patch.setter
    def patch(self, value):

        if isinstance(value, dict):
            self._patch = {key: value[key] for key in self._patch_keys}
        elif isinstance(value, list) and len(value) == 4:
            self._patch = {key: value[i] for i, key in enumerate(self._patch_keys)}
        else:
            raise ValueError(f"patch must be a dict or list, not {type(value)}")
        # make sure the correct keys are there
        print(f"Patch set to: {self._patch} for {self}")

    @property
    def refs(self):
        return self._refs

    @refs.setter
    def refs(self, value):
        if value is None:
            self._refs = None
            return

        if not (isinstance(value, list) and len(value) == self.nrefs):
            raise ValueError(f"refs should be a list of length {self.nrefs}")

        parsed_refs = []
        for ref in value:
            if isinstance(ref, imagehash.ImageHash):
                parsed_refs.append(ref)
            elif isinstance(ref, str):
                parsed_refs.append(imagehash.hex_to_hash(ref))
            else:
                raise ValueError(f"refs should either be str or ImageHash, not {type(ref)}")

        self._refs = parsed_refs

    @property
    def nrefs(self):
        return self._nrefs

    @nrefs.setter
    def nrefs(self, value):
        value = int(value)
        if not (isinstance(value, int) and value > 0):
            self._nrefs = None
            raise ValueError(f"nrefs should be a an int > 0")
        self._nrefs = value

    @property
    def idfr(self):
        return self._idfr

    @idfr.setter
    def idfr(self, value):
        self._idfr = str(value)

    """Feature extractor"""

    def extract(self, data):
        phash = self._extract(data)
        dist = min(abs(ref - phash) for ref in self.refs)
        return dist

    def _extract(self, data):
        patch = [self.patch["x0"], self.patch["y0"], self.patch["x1"], self.patch["y1"]]
        crop = data.crop(box=patch)
        phash = imagehash.phash(crop)
        return phash

    """Serializable interface """

    def to_jcr(self):
        data = {
            "patch": self.patch,
            "refs": [str(ref) for ref in self.refs] if self.refs is not None else None,
            "nrefs": self.nrefs,
        }
        state = {"class": self.class2str(), "state": data}
        return state

    @classmethod
    def from_jcr(cls, jcr):
        patch, refs, nrefs, idfr = None, None, None, None
        if "patch" in jcr:
            patch = jcr["patch"]
        if "nrefs" in jcr:
            nrefs = jcr["nrefs"]
        if "refs" in jcr:
            refs = jcr["refs"]
        if "idfr" in jcr:
            refs = jcr["idfr"]

        return cls(patch=patch, refs=refs, nrefs=nrefs, idfr=idfr)

    """Buildable interface"""

    def build(self, data):
        refs = []
        chosen_samples = random.choices(data, k=self.nrefs)
        for sample in chosen_samples:
            ref = self._extract(sample)
            refs.append(ref)
        self.refs = refs

    def is_built(self):
        return self.refs is not None and len(self.refs) == self.nrefs

    def __str__(self):
        return f"{self.class2str()} ({self.idfr})"
