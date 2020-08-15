import requests
from pathlib import Path

from raymon.io import load_secret
from raymon.exceptions import NetworkException
from raymon.log import Logger


class RaymonAPI(Logger):
    def __init__(self, url="http://localhost:8000",
                 context="your_service_v1.1",
                 project_id="default",
                 secret_fpath=Path("~/.raymon/secret.json").expanduser()):
        super().__init__(context=context, project_id=project_id)
        self.url = url  
        # self.headers = {'Content-type': 'application/msgpack'}
        self.headers = {'Content-type': 'application/json'}
        self.secret = load_secret(secret_fpath)
        self.login()
             

    """
    Functions related to logging of rays
    """
    def log(self, ray_id, peephole, data):
        # print(f"Logging Raymon Datatype...{type(data)}", flush=True)
        msg = self.format(ray_id=ray_id, peephole=peephole, data=data.to_dict())
        resp = requests.post(f"{self.url}/projects/{self.project_id}/ingest",
                             json=msg,
                             headers=self.headers)
        self.logger.debug(f"{ray_id} logged at {peephole}: {resp.status_code} - {resp.text}")
    
    
    def tag(self, ray_id, tags):
        # TODO validate tags
        resp = requests.post(f"{self.url}/projects/{self.project_id}/rays/{ray_id}/tags",
                             json=tags,
                             headers={'Content-type': 'application/json'})
        self.logger.debug(f"{ray_id} tagged: {resp.status_code} - {resp.text}")
        
        
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


