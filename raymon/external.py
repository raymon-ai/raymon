import requests
from pathlib import Path
import pendulum

from raymon.auth import load_secret
from raymon.exceptions import NetworkException
from raymon.log import setup_logger


class RaymonAPI():
    def __init__(self,
                 url="http://localhost:8000",
                 project_id="default",
                 secret_fpath=None):
        
        self.url = url  
        self.project_id = project_id
        self.logger = setup_logger(stdout=True)
        
        self.headers = {'Content-type': 'application/json'}
        self.secret = load_secret(project_name=project_id, fpath=secret_fpath)
        self.login()

             
    def structure(self, ray_id, peephole, data):
        return {
            'timestamp': str(pendulum.now('utc')),
            'ray_id': str(ray_id),
            'peephole': peephole,
            'data': data,
            'project_id': self.project_id
        }
            
    """
    Functions related to logging of rays
    """
    def info(self, ray_id, text):
        # print(f"Logging Raymon Datatype...{type(data)}", flush=True)
        jcr = self.structure(ray_id=ray_id, peephole=None, data=text)
        self.logger.info(text, extra=jcr)
        resp = requests.post(f"{self.url}/projects/{self.project_id}/ingest",
                             json=jcr,
                             headers=self.headers)
        status = 'OK' if resp.ok else f'ERROR: {resp.status_code}'
        self.logger.info(f"Logged info. Status: {status}", extra=jcr)
        
    def log(self, ray_id, peephole, data):
        # print(f"Logging Raymon Datatype...{type(data)}", flush=True)
        jcr = self.structure(ray_id=ray_id, peephole=peephole, data=data.to_jcr())
        self.logger.info(f"Logging data at {peephole}", extra=jcr)
        resp = requests.post(f"{self.url}/projects/{self.project_id}/ingest",
                             json=jcr,
                             headers=self.headers)
        status = 'OK' if resp.ok else f'ERROR: {resp.status_code}'
        self.logger.info(f"Data logged at {peephole}. Status: {status}", extra=jcr)
    
    
    def tag(self, ray_id, tags):
        # TODO validate tags
        jcr = self.structure(ray_id=ray_id, peephole=None, data=tags)
        resp = requests.post(f"{self.url}/projects/{self.project_id}/rays/{ray_id}/tags",
                             json=tags,
                             headers={'Content-type': 'application/json'})
        status = 'OK' if resp.ok else f'ERROR: {resp.status_code}'
        self.logger.info(f"Ray tagged. Status: {status}", extra=jcr)
        
        
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
    
    """
    Functions related to Authentication
    """
    def login(self):
        data = {"audience": self.secret['audience'],
                "grant_type": self.secret['grant_type'],
                "client_id": self.secret['client_id'],
                "client_secret": self.secret['client_secret']
                }

        route = f"{self.secret['auth_url']}/oauth/token"
        resp = requests.post(route, data=data)
        if resp.status_code != 200:
            raise NetworkException(f"Can not login to Raymon service: \n{resp.text}")
        else:
            token_data = resp.json()
            self.token = token_data['access_token']
            self.headers['Authorization'] = f'Bearer {self.token}'


