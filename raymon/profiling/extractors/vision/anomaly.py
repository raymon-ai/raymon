# https://github.com/onnx/tutorials#converting-to-onnx-format
# https://pytorch.org/tutorials/advanced/super_resolution_with_onnxruntime.html

import onnxruntime
import pkg_resources

import numpy as np
import base64
from PIL import Image
from collections.abc import Iterable

from raymon.profiling.extractors.structured.kmeans import KMeansOutlierScorer


class DN2AnomalyScorer(KMeansOutlierScorer):
    def __init__(self, k=16, clusters=None, dist="euclidean"):
        super().__init__(k=k, clusters=clusters, dist=dist)
        # model link - https://github.com/onnx/models/tree/master/vision/classification/mobilenet
        self.mobilenet = onnxruntime.InferenceSession(
            pkg_resources.resource_filename("raymon", "models/mobilenetv2-7.onnx")
        )
        self.size = (224, 224)

    def batches(self, loaded_data, batch_size):
        l = len(loaded_data)
        for start in range(0, l, batch_size):
            images = loaded_data[start : min(start + batch_size, l)]
            batch_numpy = np.zeros((len(images), 3, self.size[0], self.size[1]), dtype=np.float32)
            for i, img in enumerate(images):
                img_np = self.preprocess(img)
                batch_numpy[i, :] = img_np
            yield batch_numpy.astype(np.float32)

    def preprocess(self, pil_img):
        if isinstance(pil_img, np.ndarray):
            pil_img = Image.fromarray(pil_img)
        pil_resized = pil_img.resize(size=self.size)
        np_img = np.array(pil_resized) / 255
        np_std = (np_img - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
        np_moved = np.moveaxis(np_std, 2, 0)
        return np_moved.astype(np.float32)

    def extract(self, data):
        if not (isinstance(data, Image.Image) or isinstance(data, np.ndarray)):
            raise ValueError(f"type of data must be PIL.Image.Image or numpy.ndarray, not {type(data)}")
        input_np = np.zeros((1, 3, self.size[0], self.size[1]), dtype=np.float32)
        input_np[0, :] = self.preprocess(data)
        input_img = {self.mobilenet.get_inputs()[0].name: input_np}
        feats = self.mobilenet.run(None, input_feed=input_img)
        return super().extract(data=feats[0])

    def build(self, data, batch_size=16):
        if not isinstance(data, Iterable):
            raise ValueError(f"type of the data must be Iterable")
        embeddings = np.zeros((len(data), 1000))
        for batch_idx, batch_np in enumerate(self.batches(data, batch_size=batch_size)):
            input_images = {self.mobilenet.get_inputs()[0].name: batch_np}
            extracted = self.mobilenet.run(None, input_feed=input_images)[0]
            start_idx = batch_idx * batch_size
            stop_idx = start_idx + len(extracted)
            embeddings[start_idx:stop_idx] = extracted

        indexes = np.where(np.sum(np.abs(embeddings), axis=1) != 0)
        embeddings = embeddings[indexes]
        super().build(data=embeddings)

    """Serializable interface"""

    def to_jcr(self):
        b64 = base64.b64encode(self.clusters).decode()
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
