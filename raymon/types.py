import json
import io
from abc import abstractmethod
from pydoc import locate
import msgpack
import numpy as np
import pandas as pd
import base64
import ast
from PIL import Image as PILImage


class DataFormatException(Exception):
    pass


class RaymonDataType:
    @abstractmethod
    def to_jcr(self):
        pass

    def to_json(self):
        return json.dumps(self.to_jcr())

    def to_msgpack(self):
        return msgpack.packb(self.to_jcr())

    def class2str(self):
        module = str(self.__class__.__module__)
        classname = str(self.__class__.__name__)
        return f"{module}.{classname}"


class Image(RaymonDataType):
    def __init__(self, data):
        self.validate(data)
        self.data = data

    def validate(self, data):
        # Validate 3 channels
        if not isinstance(data, PILImage.Image):
            raise DataFormatException("Image shoud be a PIL Image")
        return True

    def to_jcr(self):
        img_byte_arr = io.BytesIO()
        # We'll save the image as JPEG. This is not lossless, but it is saves as the highest JPEG quality. This is 25 times faster than dumping as lossless PNG, and results in a size of only 1/5th the size, before b64 encoding.
        # Measurements: PNG: 3.767667055130005s, 4008037 bytes -- PNG: 3.767667055130005s, 4008037 bytes
        # For impact on algorithms see "On the Impact of Lossy Image and Video Compression on the Performance of Deep Convolutional Neural Network Architectures" (https://arxiv.org/abs/2007.14314), although this paper takes jpeg quality 95 as highest quality.
        self.data.save(img_byte_arr, format="jpeg", quality=95)
        img_byte_arr = img_byte_arr.getvalue()
        b64 = base64.b64encode(img_byte_arr).decode()

        data = {"type": self.class2str(), "params": {"data": b64}}
        return data

    @classmethod
    def from_jcr(cls, params):
        b64 = params["data"]
        img_byte_arr = io.BytesIO(base64.decodebytes(b64.encode()))
        img = PILImage.open(img_byte_arr)
        return cls(data=img)


class ImageRGB(RaymonDataType):
    def __init__(self, data):
        data = np.array(data)
        self.validate(data)
        self.data = data

    def validate(self, data):
        # Validate 3 channels
        if len(data.shape) != 3:
            raise DataFormatException("Image array should have 3 axis: Widht, Height and Channels")
        if not (data.shape[2] == 3 or data.shape[2] == 4):
            raise DataFormatException("Image shoud have width, height and 3 channels")
        return True

    def to_jcr(self):
        # img =
        # img_byte_arr = io.BytesIO()
        # roi_img.save(img_byte_arr, format='PNG')
        # img_byte_arr = img_byte_arr.getvalue()

        b64 = base64.b64encode(self.data).decode()
        shape = self.data.shape
        dtype = self.data.dtype
        data = {"type": self.class2str(), "params": {"data": b64, "shape": str(shape), "dtype": str(dtype)}}
        return data

    @classmethod
    def from_jcr(cls, params):
        shape = ast.literal_eval(params["shape"])
        dtype = params["dtype"]
        b64 = params["data"]
        nprest = np.frombuffer(base64.decodebytes(b64.encode()), dtype=str(dtype)).reshape(shape)
        return cls(data=nprest)


class ImageGrayscale(RaymonDataType):
    def __init__(self, data):
        data = np.array(data)
        self.validate(data)
        self.data = data

    def validate(self, data):
        # Validate 3 channels
        if len(data.shape) != 2:
            raise DataFormatException("Image array should have 2 axis: Width and height")
        return True

    def to_jcr(self):
        b64 = s = base64.b64encode(self.data).decode()
        shape = self.data.shape
        dtype = self.data.dtype
        data = {"type": self.class2str(), "params": {"data": b64, "shape": str(shape), "dtype": str(dtype)}}
        return data

    @classmethod
    def from_jcr(cls, params):
        shape = ast.literal_eval(params["shape"])
        dtype = params["dtype"]
        b64 = params["data"]
        nprest = np.frombuffer(base64.decodebytes(b64.encode()), dtype=str(dtype)).reshape(shape)
        return cls(data=nprest)


class Numpy(RaymonDataType):
    def __init__(self, data):
        data = np.array(data)
        self.validate(data)
        self.data = data

    def validate(self, data):
        return True

    def to_jcr(self):
        b64 = base64.b64encode(self.data).decode()
        shape = self.data.shape
        dtype = self.data.dtype
        data = {"type": self.class2str(), "params": {"data": b64, "shape": str(shape), "dtype": str(dtype)}}
        return data

    @classmethod
    def from_jcr(cls, params):
        shape = ast.literal_eval(params["shape"])
        dtype = params["dtype"]
        b64 = params["data"]
        nprest = np.frombuffer(base64.decodebytes(b64.encode()), dtype=str(dtype)).reshape(shape)
        return cls(data=nprest)


class Vector(RaymonDataType):
    def __init__(self, data, names=None):
        self.validate(data, names)
        self.data = np.array(data)
        self.names = np.array(names) if not names is None else None

    def validate(self, data, names):
        if len(data.shape) != 1:
            raise DataFormatException("Vector data must be a 1D array")
        if names is not None and len(data) != len(names):
            raise DataFormatException("Vector data and names must have same shape")
        return True

    def to_jcr(self):
        data = {
            "type": self.class2str(),
            "params": {
                "data": self.data.tolist(),
                "names": self.names.tolist(),
            },
        }
        return data


class Series(RaymonDataType):
    def __init__(self, data):
        self.validate(data)
        self.data = data

    def validate(self, data):
        if not isinstance(data, pd.Series):
            raise DataFormatException("Data should be a Pandas Series")
        return True

    def to_jcr(self):
        data = {
            "type": self.class2str(),
            "params": {
                "data": json.loads(self.data.to_json()),
            },
        }
        return data

    @classmethod
    def from_jcr(cls, jcr):
        series = pd.Series(**jcr)
        return cls(series)


class DataFrame(RaymonDataType):
    def __init__(self, data):
        self.validate(data)
        self.data = data

    def validate(self, data):
        if not isinstance(data, pd.DataFrame):
            raise DataFormatException("Data should be a Pandas DataFrame")
        return True

    def to_jcr(self):
        data = {
            "type": self.class2str(),
            "params": {
                "data": json.loads(self.data.to_json()),
            },
        }
        return data

    @classmethod
    def from_jcr(cls, jcr):
        frame = pd.read_json(json.dumps(jcr["data"]))
        return cls(frame)


class JCR(RaymonDataType):
    def __init__(self, data):
        self.validate(data)
        self.data = data

    def validate(self, data):
        try:
            json.dumps(data)
        except TypeError as exc:
            raise DataFormatException(f"{exc}")
        return True

    def to_jcr(self):
        data = {
            "type": self.class2str(),
            "params": {
                "data": self.data,
            },
        }
        return data

    @classmethod
    def from_jcr(cls, jcr):
        return cls(jcr)


class Number(RaymonDataType):
    def __init__(self, data):
        self.validate(data)
        self.data = data

    def validate(self, data):
        if not (isinstance(data, int) or isinstance(data, float)):
            raise DataFormatException("Data should be int or float")
        return True

    def to_jcr(self):
        data = {
            "type": self.class2str(),
            "params": {
                "data": self.data,
            },
        }
        return data

    @classmethod
    def from_jcr(cls, jcr):
        data = jcr["data"]
        return cls(data)


class String(RaymonDataType):
    def __init__(self, data):
        self.validate(data)
        self.data = data

    def validate(self, data):
        if not isinstance(data, str):
            raise DataFormatException("Data should be str")
        return True

    def to_jcr(self):
        data = {
            "type": self.class2str(),
            "params": {
                "data": self.data,
            },
        }
        return data

    @classmethod
    def from_jcr(cls, jcr):
        data = jcr["data"]
        return cls(data)


class Histogram(RaymonDataType):
    def __init__(self, counts, edges, names=None, normalized=False, **kwargs):
        counts = np.array(counts)
        edges = np.array(edges)
        self.validate(counts, edges)
        self.counts = counts
        self.edges = edges
        self.names = names
        self.normalized = normalized
        self.kwargs = kwargs

    def validate(self, counts, edges):
        if len(counts.shape) != 1:
            raise DataFormatException("counts must be a 1D array")
        if len(counts) != len(edges) - 1:
            raise DataFormatException("len(counts) must be len(edges)-1")
        return True

    def to_jcr(self):
        data = {
            "type": self.class2str(),
            "params": {
                "counts": self.counts.tolist(),
                "names": self.names,
                "edges": self.edges.tolist(),
            },
        }
        return data


def load_jcr(jcr):
    params = jcr["params"]
    dtype = jcr["type"]
    type_class = locate(dtype)
    if type_class is None:
        raise NameError(f"Could not locate {dtype}")

    loaded = type_class.from_jcr(params)
    return loaded


def from_msgpack(data):
    loaded_data = msgpack.unpackb(data, raw=False)
    return load_jcr(loaded_data)
