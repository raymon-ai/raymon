import pendulum
import logging
import sys
import msgpack
# import msgpack_numpy
# msgpack_numpy.patch()
import requests

from raymon.logger import setup_logger
    
# TODO: make ABC with interface methods

class FileLogger:
    
    def __init__(self, fpath='/tmp/raymon.log', stdout=True, context="your_service_v1.1"):
        self.logger = setup_logger(context=context, fname=fpath, stdout=stdout, )
        
    def format(self, ray_id, peephole, data, dtype):
        return {
            'timestamp': str(pendulum.now()),
            'ray_id': ray_id,
            'peephole': peephole,
            'data': data,
            'dtype': dtype,
        }
    """
    Functions related to logging of rays
    """
    def log_text(self, ray_id, peephole, data):
        msg = self.format(ray_id=ray_id, peephole=peephole, data=data, dtype='text')
        self.logger.info(msg)
        
    def log_numpy(self, ray_id, peephole, data):
        # print(f"Logging image of type: {type(data)}")
        # data_enc = msgpack.packb(data.tolist())
        msg = self.format(ray_id=ray_id, peephole=peephole, data=data.tolist(), dtype='numpy')
        self.logger.debug(msg)

    
class APILogger:
    def __init__(self, url="http://localhost:8000", 
                 user="raymond", 
                 password="pass", 
                 context="your_service_v1.1"):
        self.url = url  # TODO: set up api connection
        self.headers = {'Content-type': 'application/msgpack',
                        'Authorization': 'YOURTOKEN'}
        
        self.logger = setup_logger(context=context, stdout=True)

    def format(self, ray_id, peephole, data, dtype):
        return {
            'timestamp': str(pendulum.now()),
            'ray_id': ray_id,
            'peephole': peephole,
            'data': data,
            'dtype': dtype,
        }
    """
    Functions related to logging of rays
    """
        
    def log_text(self, ray_id, peephole, data):
        print(f"Logging TEXT...", flush=True)
        msg = self.format(ray_id=ray_id, peephole=peephole, data=data, dtype='text')
        msg_data = msgpack.packb(msg)
        resp = requests.post(f"{self.url}/ingest_text",
                             data=msg_data,
                             headers=self.headers)
        print(resp)
        self.logger.debug(f"{ray_id} logged at {peephole}: Text")

    def log_numpy(self, ray_id, peephole, data):
        print(f"Logging NUMPY...{type(data)}", flush=True)
        msg = self.format(ray_id=ray_id, peephole=peephole, data=data.tolist(), dtype='numpy')
        msg_data = msgpack.packb(msg)
        resp = requests.post(f"{self.url}/ingest_image",
                             data=msg_data,
                             headers=self.headers)
        self.logger.debug(f"{ray_id} logged at {peephole}: {resp}")


# def callable_wrapper(callable, log_func, ray_peephole, *args, kwargs):
#     img = callable(*args, **kwargs)
#     ray_mgr.log_image(image=img, peephole=ray_peephole)
#     return img
    
