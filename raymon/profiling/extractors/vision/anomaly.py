# https://github.com/onnx/tutorials#converting-to-onnx-format
# https://pytorch.org/tutorials/advanced/super_resolution_with_onnxruntime.html

import onnxruntime

import numpy as np
import base64
from PIL import Image
import os

from raymon.profiling.extractors.structured.kmeans import KMeansOutlierScorer

class DN2AnomalyScorer(KMeansOutlierScorer):
    def __init__(self, k=16, size=None, clusters=None, dist="euclidean"):
        super().__init__(k=k, clusters=clusters, dist=dist)
        # model link - https://github.com/onnx/models/tree/master/vision/classification/mobilenet
        self.mobilenet = onnxruntime.InferenceSession("raymon/models/mobilenetv2-7.onnx")
        self.size = size
                
    def preprocess_data(self, pil_img):
        # resize pil image 
        img = pil_img.resize(size=(224, 224))
        # Convert pil_image into numpy
        numpy_img = np.array( img, dtype=np.float32 ) 
        # normalize between 0.0 and 1.0
        numpy_img = numpy_img / 255
        # reshape image for onnx model
        numpy_img = numpy_img.reshape( [1, 3, 224, 224] ) 
        return numpy_img
    
    def preparation_batch_data(self, pil_img_list, batch_size):
        # Our data is a list containing pil images
        # Convert this image to numpy
        # Make batches from data and store them in dataloader
        dataloader = []
        for i in range(0, len(pil_img_list), batch_size):
            # if we arrive the end of the list, we have to adjust the shape of the array, 
            if i+batch_size>len(pil_img_list):
                batch_numpy = np.zeros((len(pil_img_list)-i, 3, 224, 224))
            # Otherwise the shape of the array is (batch_size, 3, 224, 224).
            else:
                # Create zero numpy array with batch shape
                batch_numpy = np.zeros((batch_size, 3, 224, 224))
            # Make batches    
            for k in range(i, i+batch_size):
                # Avoid to exceed the length of the pil_img_list (list index out of range)
                if k==len(pil_img_list):
                    break
                x = 0 
                # Convert pil image and do other preprocessings
                numpy_img = self.preprocess(pil_img_list[k])
                batch_numpy[x, :, :, :] = numpy_img
                x+=1 
            dataloader.append(batch_numpy)
        return dataloader

    def extract(self, data):
        if not isinstance(data, Image.Image):
            raise ValueError(f"type of data must be PIL.Image.Image, not {data.shape}")
        numpy_img = {self.mobilenet.get_inputs()[0].name: self.preprocess_data(data)}
        feats = self.mobilenet.run(None, input_feed=numpy_img)
        return super().extract(data=feats) 

    def build(self, data, batch_size=16): 
        if not isinstance(data, list):
            raise ValueError(f"type of the data must be list")
        dataloader = self.preparation_batch_data(data, batch_size)               
        embeddings = np.zeros((len(data), 1000))
        for batchidx, batch_numpy in enumerate(dataloader):
            batch_numpy = np.array( batch_numpy, dtype=np.float32 )
            ort_inputs2 = {self.mobilenet.get_inputs()[0].name: batch_numpy}
            components = self.mobilenet.run(None, input_feed=ort_inputs2)
            startidx = batchidx * batch_size
            stopidx = startidx + len(components[0])
            embeddings[startidx:stopidx, :] = components[0]

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