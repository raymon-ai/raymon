import logging
import sys
import pendulum

from raymon.ray import Ray

class ContextFilter(logging.Filter):
    def __init__(self, context):
        self.context = context

    def filter(self, record):
        record.context = self.context
        return True


class Logger:
    
    def ray(self, ray_id=None):
        return Ray(logger=logger, ray_id=ray_id)
        

    def format(self, ray_id, peephole, data, dtype):
        return {
            'timestamp': str(pendulum.now()),
            'ray_id': ray_id,
            'peephole': peephole,
            'data': data,
            'dtype': dtype,
        }


class FileLogger(Logger):

    def __init__(self, fpath='/tmp/raymon.log', stdout=True, context="your_service_v1.1"):
        self.logger = setup_logger(context=context, fname=fpath, stdout=stdout, )

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


class APILogger(Logger):
    def __init__(self, url="http://localhost:8000",
                 user="raymond",
                 password="pass",
                 context="your_service_v1.1"):
        self.url = url  # TODO: set up api connection
        self.headers = {'Content-type': 'application/msgpack',
                        'Authorization': 'YOURTOKEN'}
        self.logger = setup_logger(context=context, stdout=True)

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


def setup_logger(context, fname=None, stdout=True):
    # Set up the raymon logger
    logger = logging.getLogger("Raymon")
    logger.setLevel(logging.DEBUG)
    # Set level to debug -- will use debug messages for binary data
    logger.addFilter(ContextFilter(context))
    formatter = logging.Formatter("{asctime} - {name} - {context} - {message}", style='{')

    if fname is not None:
        # Add a file handler
        fh = logging.FileHandler(fname)
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)

    if stdout:
        print(f"Adding stout")
        # Add a stderr handler -- Do not send DEBUG messages to there (will contain binary data)
        sh = logging.StreamHandler(stream=sys.stdout)
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)
        logger.addHandler(sh)
    return logger
