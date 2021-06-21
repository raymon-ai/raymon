# https://github.com/onnx/tutorials#converting-to-onnx-format
# https://pytorch.org/tutorials/advanced/super_resolution_with_onnxruntime.html

import onnxruntime
import pkg_resources

import numpy as np
import base64
from PIL import Image
from collections.abc import Iterable

from raymon.profiling.extractors.structured.kmeans import KMeansOutlierScorer

model_path=pkg_resources.resource_filename("raymon", "models/mobilenetv2-7.onnx")

class DN2AnomalyScorer(KMeansOutlierScorer):
    def __init__(self, k=16, size=None, clusters=None, dist="euclidean"):
        super().__init__(k=k, clusters=clusters, dist=dist)
        # model link - https://github.com/onnx/models/tree/master/vision/classification/mobilenet
        self.mobilenet = onnxruntime.InferenceSession(model_path)
        self.size = size
                
    def preprocess(self, img):
        # Convert pil_image into numpy
        numpy_img = np.array( img, dtype=np.float32 ) 
        # resize image 
        numpy_img = np.resize(numpy_img, (224, 224, 3))
        # reshape image for onnx model
        numpy_img = numpy_img.reshape( [1, 3, 224, 224] ) 
        return numpy_img
    
    def prepare_batch(self, images, batch_size):
        # Our data is a list containing pil images
        # Convert this image to numpy
        # Make batches from data and store them in dataloader
        dataloader = []
        for i in range(0, len(images), batch_size):
            # if we arrive the end of the list, we have to adjust the shape of the array, 
            if i+batch_size>len(images):
                batch_numpy = np.zeros((len(images)-i, 3, 224, 224))
            # Otherwise the shape of the array is (batch_size, 3, 224, 224).
            else:
                # Create zero numpy array with batch shape
                batch_numpy = np.zeros((batch_size, 3, 224, 224))
            # Make batches    
            for k in range(i, i+batch_size):
                # Avoid to exceed the length of the images (list index out of range)
                if k==len(images):
                    break
                x = 0 
                # Convert pil image and do other preprocessings
                numpy_img = self.preprocess(images[k])
                batch_numpy[x, :, :, :] = numpy_img
                x+=1 
            dataloader.append(batch_numpy)
        return dataloader

    def extract(self, data):
        if not isinstance(data, Image.Image) and not isinstance(data, np.ndarray):
            raise ValueError(f"type of data must be PIL.Image.Image or numpy.ndarray, not {type(data)}")
        numpy_img = {self.mobilenet.get_inputs()[0].name: self.preprocess(data)}
        feats = self.mobilenet.run(None, input_feed=numpy_img)
        return super().extract(data=feats[0]) 

    def build(self, data, batch_size=16): 
        if not isinstance(data, Iterable):
            raise ValueError(f"type of the data must be Iterable")
        dataloader = self.prepare_batch(data, batch_size)               
        embeddings = np.zeros((len(data), 1000))
        for batchidx, batch_numpy in enumerate(dataloader):
            batch_numpy = np.array( batch_numpy, dtype=np.float32 )
            ort_inputs2 = {self.mobilenet.get_inputs()[0].name: batch_numpy}
            extracted = self.mobilenet.run(None, input_feed=ort_inputs2)
            startidx = batchidx * batch_size
            stopidx = startidx + len(extracted[0])
            embeddings[startidx:stopidx, :] = extracted[0]

        indexes = np.where(np.sum(np.abs(embeddings), axis=1)!=0)
        embeddings = embeddings[indexes]
        super().build(data=embeddings)

    """Serializable interface"""

    def to_jcr(self):
        b64 = base64.b64encode(self.clusters).decode()
        diststr = [k for k, v in self.dist_choices.items() if v == self.dist][0]
        data = {"clusters": b64, "k": self.k, "dist": diststr, "size": self.size}
        state = {"class": self.class2str(), "state": data}
        return state

    @classmethod
    def from_jcr(cls, jcr):
        k = jcr["k"]
        b64 = jcr["clusters"]
        dist = jcr["dist"]
        size = jcr["size"]
        clusters = np.frombuffer(base64.decodebytes(b64.encode()), dtype=np.float64).reshape((k, -1))
        return cls(k=k, size=size, clusters=clusters, dist=dist)



