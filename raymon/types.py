import json
import io
from abc import ABC, abstractmethod
from pydoc import locate
import msgpack
import numpy as np
import pandas as pd
import base64
import ast
from PIL import Image as PILImage
from raymon.globals import Serializable


class RaymonDataType(Serializable, ABC):
    def to_json(self):
        return json.dumps(self.to_jcr())

    def to_msgpack(self):
        return msgpack.packb(self.to_jcr())

    def class2str(self):
        module = str(self.__class__.__module__)
        classname = str(self.__class__.__name__)
        return f"{module}.{classname}"


class Image(RaymonDataType):
    def __init__(self, data, lossless=False):
        self.validate(data=data, lossless=lossless)
        self.data = data
        self.lossless = lossless

    def validate(self, data, lossless):
        # Validate 3 channels
        if not isinstance(data, PILImage.Image):
            raise ValueError("Image shoud be a PIL Image")
        if not isinstance(lossless, bool):
            raise ValueError("lossless should be boolean")
        return True

    def to_jcr(self):
        img_byte_arr = io.BytesIO()
        if self.lossless:
            self.data.save(img_byte_arr, format="png")
        else:
            # We'll save the image as JPEG. This is not lossless, but it is saves as the highest JPEG quality. This is 25 times faster than dumping as lossless PNG, and results in a size of only 1/5th the size, before b64 encoding.
            # Measurements: PNG: 3.767667055130005s, 4008037 bytes -- PNG: 3.767667055130005s, 4008037 bytes
            # For impact on algorithms see "On the Impact of Lossy Image and Video Compression on the Performance of Deep Convolutional Neural Network Architectures" (https://arxiv.org/abs/2007.14314), although this paper takes jpeg quality 95 as highest quality.
            self.data.save(img_byte_arr, format="jpeg", quality=95)
        img_byte_arr = img_byte_arr.getvalue()
        b64 = base64.b64encode(img_byte_arr).decode()

        data = {"type": self.class2str(), "params": {"data": b64, "lossless": self.lossless}}
        return data

    @classmethod
    def from_jcr(cls, params):
        b64 = params["data"]
        img_byte_arr = io.BytesIO(base64.decodebytes(b64.encode()))
        img = PILImage.open(img_byte_arr)
        return cls(data=img)


class Numpy(RaymonDataType):
    def __init__(self, data):
        self.validate(data)
        self.data = data

    def validate(self, data):
        if not isinstance(data, np.ndarray):
            raise ValueError(f"Data must bu of type numpy.ndarray, not {type(data)}.")
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


class Series(RaymonDataType):
    def __init__(self, data):
        self.validate(data)
        self.data = data

    def validate(self, data):
        if not isinstance(data, pd.Series):
            raise ValueError("Data should be a Pandas Series")
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
            raise ValueError("Data should be a Pandas DataFrame")
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


class Native(RaymonDataType):
    def __init__(self, data):
        self.validate(data)
        self.data = data

    def validate(self, data):
        try:
            json.dumps(data)
        except TypeError as exc:
            raise ValueError(f"{exc}")
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
        return cls(jcr["data"])


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
