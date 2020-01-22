import numpy as np
import msgpack
from abc import abstractmethod


class DataFormatException(Exception):
    pass


class RaymonDataType:

    @abstractmethod
    def valid(self, data):
        pass

    @abstractmethod
    def to_json(self):
        pass

    @abstractmethod
    def viz(self, **kwargs):
        pass

    def to_msgpack(self):
        return msgpack.packb(self.to_json())


class ImageRGB(RaymonDataType):
    def __init__(self, data):
        data = np.array(data)
        if self.valid(data):
            self.data = data

    def valid(self, data):
        # Validate 3 channels
        if len(data.shape) != 3:
            raise DataFormatException("Image array should have 3 axis: Widht, Height and Channels")
        if data.shape[2] != 3:
            raise DataFormatException("Image shoud have width, height and 3 channels")
        return True

    def to_json(self):
        data = {
            'type': self.__class__.__name__,
            'params': {
                'data': self.data.tolist()
            }
        }
        return data

    def visualize(self, **kwargs):
        data = {
            'type': 'bokeh',
            'data': {
                # TODO
            }
        }
        return data


class ImageGrayscale(RaymonDataType):
    def __init__(self, data):
        data = np.array(data)
        if self.valid(data):
            self.data = data

    def valid(self, data):
        # Validate 3 channels
        if len(data.shape) != 2:
            raise DataFormatException("Image array should have 2 axis: Width and height")
        return True

    def to_json(self):
        data = {
            'type': self.__class__.__name__,
            'params': {
                'data': self.data.tolist()
            }
        }
        return data

    def visualize(self, **kwargs):
        data = {
            'type': 'bokeh',
            'data': {
                # TODO
            }
        }
        return data


class Numpy(RaymonDataType):
    def __init__(self, data):
        data = np.array(data)
        if self.valid(data):
            self.data = data

    def valid(self, data):
        # # Validate 3 channels
        # if len(data.shape) != 2:
        #     raise DataFormatException("Image array should have 2 axis: Width and height")
        return True

    def to_json(self):
        data = {
            'type': self.__class__.__name__,
            'params': {
                'data': self.data.tolist()
            }
        }
        return data


class Vector(RaymonDataType):
    def __init__(self, data, names=None):
        if self.valid(data, names):
            self.data = np.array(data)
            self.names = np.array(names) if not names is None else None

    def valid(self, data, names):
        print(f"Vector validation input: Data {data}, names {names}")
        # Validate 3 channels
        if len(data.shape) != 1:
            raise DataFormatException("Vector data must be a 1D array")
        if names is not None and data.shape != names.shape:
            raise DataFormatException("Vector data and names must have same shape")
        return True

    def to_json(self):
        data = {
            'type': self.__class__.__name__,
            'params': {
                'data': self.data.tolist(),
                'names': self.names.tolist(),
            }

        }
        return data


class Text(RaymonDataType):
    def __init__(self, text):
        if self.valid(text):
            self.text = text

    def valid(self, text):
        # Validate 3 channels
        if not isinstance(text, str):
            raise DataFormatException("text must be str")
        return True

    def to_json(self):
        data = {
            'type': self.__class__.__name__,
            'params': {
                'text': self.text,
            }
        }
        return data


DTYPES = {
    'ImageRGB': ImageRGB,
    'ImageGrayscale': ImageGrayscale,
    'Numpy': Numpy,
    'Vector': Vector,
    'Text': Text
}


def from_msgpack(data):
    loaded_data = msgpack.unpackb(data, raw=False)
    params = loaded_data['params']
    dtype = loaded_data['type']
    return DTYPES[dtype](**params)
