# %% 
import requests
import json
from pathlib import Path

from raymon.io import load_secret

secret_fpath = Path("~/.raymon/secret.json").expanduser()


class Testing:
    
    def __init__(self):
        self.headers = {'Content-type': 'application/json'}
        self.secret = load_secret(secret_fpath)

    def connect(self):
        body = {"audience": self.secret['audience'],
                "grant_type": "client_credentials",
                "client_id": self.secret['client_id'],
                "client_secret": self.secret['client_secret'],
                }
        print(f"Request body: {body}")
        resp = requests.post(url=self.secret['login_url'], headers=self.headers, json=body)
        return resp

test = Testing()
resp = test.connect()
resp.json()
# %%
