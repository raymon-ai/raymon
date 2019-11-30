import pendulum
import logging
import sys
import msgpack
import msgpack_numpy as m
m.patch()

from raymon.logger import setup_logger


class RaymonFileLogger:
    
    def __init__(self, fpath='/tmp/raymon.log', stdout=True, context="your_service_v1.1"):
        self.logger = setup_logger(fpath, stdout=stdout, context=context)
        
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
        data_enc = msgpack.packb(data)
        msg = self.format(ray_id=ray_id, peephole=peephole, data=data_enc, dtype='numpy')
        self.logger.debug(msg)

    
class RaymonWebLogger:
    pass

# def callable_wrapper(callable, log_func, ray_peephole, *args, kwargs):
#     img = callable(*args, **kwargs)
#     ray_mgr.log_image(image=img, peephole=ray_peephole)
#     return img
    
