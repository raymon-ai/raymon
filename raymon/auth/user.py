from pathlib import Path
import json
import os
import requests
import time
import json
import pendulum
from requests.api import head
from raymon.exceptions import NetworkException, SecretException
import base64


DEFAULT_CONFIG = {
    "auth_url": "https://raymon-staging.eu.auth0.com",
    "audience": "https://staging-api.raymon.ai",
    "client_id": "O3L719qD65u8sQuxKoLNRddQekp9q2rS",
}


def save_user_config(existing, auth_endpoint, audience, client_id, token, out):
    out = Path(out)

    known_configs = existing
    # If so, check whether porject exists
    user_config = known_configs.get("user", {})
    user_config["config"] = {}
    user_config["secret"] = None

    # If exists, overwrite secret
    user_config["config"]["auth_url"] = auth_endpoint
    user_config["config"]["audience"] = audience
    user_config["config"]["client_id"] = client_id
    user_config["secret"] = token

    # Save secret
    known_configs["user"] = user_config
    with open(out, "w") as f:
        json.dump(known_configs, fp=f, indent=4)


def load_user_credentials(credentials):

    # HIGHEST PRIORITY 0: specified file path
    # Check whether file and project_name are specified, try loading it.
    try:
        secret = credentials.get("user", {}).get("secret", None)
        config = credentials.get("user", {}).get("config", {})
        config = verify_user(config)
        print(f"User secret loaded.")
        return config, secret
    except Exception as exc:
        print(f"Could not load user secret. {type(exc)}({exc})")
        raise SecretException(f"Could not load login config. Please initialize user config file.")


def verify_user(config):
    keys = ["auth_url", "audience", "client_id"]
    for key in keys:
        assert config[key] is not None
        assert isinstance(config[key], str)
    return config


def token_ok(token):
    if token is None:
        return False
    claims = json.loads(base64.b64decode(token.split(".")[1] + "===").decode())
    expires = pendulum.from_timestamp(claims["exp"])
    ttl = expires - pendulum.now()
    if ttl.hours < 2:
        print(f"Token expired or about to expire. Logging in...")
        return False
    else:
        print(f"Token valid for {ttl.hours} more hours.")
        return True


def login_device_flow(config):
    data = dict(client_id=config["client_id"], audience=config["audience"], scope="")
    auth_url = config["auth_url"]
    headers = {"content-type": "application/x-www-form-urlencoded"}
    resp = code_request(route=f"{auth_url}/oauth/device/code", data=data, headers=headers)
    device_resp = resp.json()
    device_code = device_resp["device_code"]
    polling_interval = device_resp["interval"]

    # Poll for login
    success = False
    while not success:
        data = dict(
            client_id=config["client_id"],
            grant_type="urn:ietf:params:oauth:grant-type:device_code",
            device_code=device_code,
        )
        resp = token_request(f"{auth_url}/oauth/token", data=data, headers=headers)

        login_resp = resp.json()
        if "error" in login_resp and login_resp["error"] == "authorization_pending":
            time.sleep(polling_interval)
            print(
                f'Login required. Please visit the following URL to authenticate: {device_resp["verification_uri_complete"]}'
            )
        elif "error" in login_resp and login_resp["error"] == "access_denied":
            raise (Exception("Access Denied"))
        else:
            success = True
    token = login_resp["access_token"]
    return token


def code_request(route, data, headers):
    return requests.post(route, data=data, headers=headers)


def token_request(route, data, headers):
    return requests.post(route, data=data, headers=headers)
