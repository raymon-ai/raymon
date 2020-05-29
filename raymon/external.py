import logging
import sys
import pendulum
import requests
from pathlib import Path

from raymon.ray import Ray
from raymon.io import load_secret
from raymon.exceptions import NetworkException


class ContextFilter(logging.Filter):
    def __init__(self, context):
        self.context = context

    def filter(self, record):
        record.context = self.context
        return True


class Logger:
    def __init__(self, context, project_id):
        self.context = context
        self.project_id = project_id
    # def ray(self, ray_id=None):
    #     return Ray(logger=logger, ray_id=ray_id)
    
    def format(self, ray_id, peephole, data):
        return {
            'timestamp': str(pendulum.now()),
            'ray_id': str(ray_id),
            'peephole': peephole,
            'data': data,
            'context': self.context,
            'project_id': self.project_id,
        }


class RaymonAPI(Logger):
    def __init__(self, url="http://localhost:8000",
                 context="your_service_v1.1",
                 project_id="default",
                 secret_fpath=Path("~/.raymon/secret.json").expanduser()):
        super().__init__(context=context, project_id=project_id)
        self.url = url  
        # self.headers = {'Content-type': 'application/msgpack'}
        self.headers = {'Content-type': 'application/json'}
        self.logger = setup_logger(context=context, stdout=True)
        self.secret = load_secret(secret_fpath)
        self.login()
        
    def login(self):
        body = {"audience": self.secret['audience'],
                "grant_type": self.secret['grant_type'], 
                "client_id": self.secret['client_id'],
                "client_secret": self.secret['client_secret']
               }
        headers = {'Content-type': 'application/json'}
        resp = requests.post(url=self.secret['login_url'], headers=headers, json=body)
        if resp.status_code != 200:
            raise NetworkException(f"Can not login to Raymon service: \n{resp.json()}")
        else:
            token_data = resp.json()
            self.token = token_data['access_token']
            self.headers['Authorization'] = f'Bearer {self.token}'        

    """
    Functions related to logging of rays
    """
    def log(self, ray_id, peephole, data):
        print(f"Logging Raymon Datatype...{type(data)}", flush=True)
        msg = self.format(ray_id=ray_id, peephole=peephole, data=data.to_dict())
        resp = requests.post(f"{self.url}/ingest",
                             json=msg,
                             headers=self.headers)
        self.logger.debug(f"{ray_id} logged at {peephole}: {resp}")
    
        
    def post(self, route, data):
        resp = requests.post(f"{self.url}/{route}",
                             json=data,
                             headers=self.headers)
        return resp
    
    def get(self, route, params):
        resp = requests.get(f"{self.url}/{route}",
                            params=params,
                            headers=self.headers)
        
        return resp
        

class MockLogger(Logger):
    def __init__(self, context="testing", project_id="default"):
        super().__init__(context=context, project_di=project_id)
    """
    Functions related to logging of rays
    """

    def log(self, ray_id, peephole, data):
        pass



def setup_logger(context, fname=None, stdout=True):
    # Set up the raymon logger
    logger = logging.getLogger("Raymon")
    if len(logger.handlers) > 0:
        # Already configured
        return logger
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
        # print(f"Adding stout")
        # Add a stderr handler -- Do not send DEBUG messages to there (will contain binary data)
        sh = logging.StreamHandler(stream=sys.stdout)
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)
        logger.addHandler(sh)
    return logger

