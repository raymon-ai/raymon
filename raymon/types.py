import numpy as np
import msgpack
from abc import abstractmethod
import json
from bokeh.plotting import figure, show
from bokeh.embed import components

import matplotlib.pyplot as plt

class DataFormatException(Exception):
    pass


class RaymonDataType:

    @abstractmethod
    def valid(self, data):
        pass

    @abstractmethod
    def to_dict(self):
        pass
    
    def to_json(self):
        return json.dumps(self.to_dict())

    # @abstractmethod
    # def visualize(self, **kwargs):
    #     pass

    def to_msgpack(self):
        return msgpack.packb(self.to_dict())


class ImageRGBA(RaymonDataType):
    def __init__(self, data):
        data = np.array(data)
        if self.valid(data):
            self.data = self.convert_rgba(data)
            print(self.data.shape)

    def convert_rgba(self, data):
        if data.shape[-1] == 3:
            rgba_shape = data.shape[0:2] + (4, )
            rgba_img = np.ones(shape=rgba_shape) * 255
            rgba_img[:, :, :-1] = data
            rgba_img = rgba_img.astype(np.uint8)
            data = rgba_img
        # Bokeh expects rgba images in a weird way...
        rgba_img = rgba_img.view(dtype=np.uint32).reshape((data.shape[:2]))

        return rgba_img
        
    def valid(self, data):
        # Validate 3 channels
        if len(data.shape) != 3:
            raise DataFormatException("Image array should have 3 axis: Widht, Height and Channels")
        if not (data.shape[2] == 3 or data.shape[2] == 4):
            raise DataFormatException("Image shoud have width, height and 3 channels")
        return True

    def to_dict(self):
        data = {
            'type': self.__class__.__name__,
            'params': {
                'data': self.data.tolist()
            }
        }
        return data

    def visualize(self, json=True, **kwargs):
        p = figure(**kwargs)
        p.x_range.range_padding = p.y_range.range_padding = 0
        p.image_rgba(image=[self.data[::-1, ::-1]], x=0, y=0, dw=5, dh=5)

        if json:
            script, div = components(p, wrap_script=False)
            vue_plot = {'div': div, 'script': script}
            data = {
                'type': 'bokeh',
                'data': vue_plot
            }
            return data

        else:
            return p


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

    def to_dict(self):
        data = {
            'type': self.__class__.__name__,
            'params': {
                'data': self.data.tolist()
            }
        }
        return data


    def visualize(self, json=True, **kwargs):
        p = figure()  # tooltips=[("x", "$x"), ("y", "$y"), ("value", "@image")]
        p.x_range.range_padding = p.y_range.range_padding = 0
        p.image(image=[self.data], x=0, y=0, dw=5, dh=5, palette="Greys256")
        
        if json:
            script, div = components(p, wrap_script=False)
            vue_plot = {'div': div, 'script': script}
            data = {
                'type': 'bokeh',
                'data': vue_plot
            }
            return data

        else:
            return p

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

    def to_dict(self):
        data = {
            'type': self.__class__.__name__,
            'params': {
                'data': self.data.tolist()
            }
        }
        return data

    
    def visualize(self, json=True, **kwargs):
        data = {
            'type': 'text',
            'data': str(self.data)
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
        if names is not None and len(data) != len(names):
            raise DataFormatException("Vector data and names must have same shape")
        return True

    def to_dict(self):
        data = {
            'type': self.__class__.__name__,
            'params': {
                'data': self.data.tolist(),
                'names': self.names.tolist(),
            }

        }
        return data

    
    def visualize(self, json=True, **kwargs):
        data = {
            'type': 'text',
            'data': str(self.data)
        }
        return data



class Histogram(RaymonDataType):
    def __init__(self, counts, edges, names=None, normalized=False, **kwargs):
        counts = np.array(counts)
        edges = np.array(edges)
        if self.valid(counts, edges):
            self.counts = counts
            self.edges = edges
            self.names = names
            self.normalized = normalized
            self.kwargs = kwargs
            

    def valid(self, counts, edges):
        # Validate 3 channels
        if len(counts.shape) != 1:
            raise DataFormatException("counts must be a 1D array")
        if len(counts) != len(edges) - 1:
            raise DataFormatException("len(counts) must be len(edges)-1")
        return True

    def to_dict(self):
        data = {
            'type': self.__class__.__name__,
            'params': {
                'counts': self.counts.tolist(),
                'edges': self.edges.tolist(),
                'names': self.names,
                'edges': self.edges.tolist(),
            }

        }
        return data

    
    def visualize(self,  json=True, **kwargs):
        p = figure(**kwargs)
        p.quad(top=self.counts, bottom=0, left=self.edges[:-1], right=self.edges[1:])

        if 'x_axis_label' in self.kwargs:
            p.xaxis.axis_label = self.kwargs['x_axis_label']
        if 'y_axis_label' in self.kwargs:
            p.yaxis.axis_label = self.kwargs['y_axis_label']
        
        if json:     
            script, div = components(p, wrap_script=False)
            vue_plot = {'div': div, 'script': script}
            data = {
                'type': 'bokeh',
                'data': vue_plot
            }
            return data

        else:
            return p



class Text(RaymonDataType):
    def __init__(self, text):
        if self.valid(text):
            self.text = text

    def valid(self, text):
        # Validate 3 channels
        if not isinstance(text, str):
            raise DataFormatException("text must be str")
        return True

    def to_dict(self):
        data = {
            'type': self.__class__.__name__,
            'params': {
                'text': self.text,
            }
        }
        return data



DTYPES = {
    'ImageRGBA': ImageRGBA,
    'ImageGrayscale': ImageGrayscale,
    'Numpy': Numpy,
    'Vector': Vector,
    'Text': Text,
    'Histogram': Histogram
}

def from_json(loaded_json):
    params = loaded_json['params']
    dtype = loaded_json['type']
    return DTYPES[dtype](**params)

def from_msgpack(data):
    loaded_data = msgpack.unpackb(data, raw=False)
    return from_json(loaded_data)
