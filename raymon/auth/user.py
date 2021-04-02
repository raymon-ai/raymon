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
import webbrowser


def save_user_config(existing, auth_endpoint, audience, client_id, token, out, env):
    out = Path(out)

    known_configs = existing
    # If so, check whether project exists
    user_config = known_configs.get("user", {})
    env_config = user_config.get(env["auth_url"], {})
    env_config["config"] = {}
    env_config["secret"] = None

    # If exists, overwrite secret
    env_config["config"]["auth_url"] = auth_endpoint
    env_config["config"]["audience"] = audience
    env_config["config"]["client_id"] = client_id
    env_config["secret"] = token

    # Save secret
    user_config[env["auth_url"]] = env_config
    known_configs["user"] = user_config
    with open(out, "w") as f:
        json.dump(known_configs, fp=f, indent=4)


def load_user_credentials(credentials, env):
    print("Loading user credential...", end=" ")
    user_env = credentials.get("user", {}).get(env["auth_url"], {})
    secret = user_env.get("secret", None)
    config = user_env.get("config", env)
    config = verify_user(config)
    print(f"Done.")
    return config, secret


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
    print("Logging in...")
    data = dict(client_id=config["client_id"], audience=config["audience"], scope="")
    auth_url = config["auth_url"]
    headers = {"content-type": "application/x-www-form-urlencoded"}
    resp = code_request(route=f"{auth_url}/oauth/device/code", data=data, headers=headers)
    device_resp = resp.json()
    device_code = device_resp["device_code"]
    polling_interval = device_resp["interval"]

    # Poll for login
    success = False
    first = True
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
            if first:
                webbrowser.open_new_tab(device_resp["verification_uri_complete"])
                first = False
        elif "error" in login_resp and login_resp["error"] == "access_denied":
            raise (NetworkException("Access Denied"))
        else:
            success = True
    token = login_resp["access_token"]
    return token


def code_request(route, data, headers):
    return requests.post(route, data=data, headers=headers)


def token_request(route, data, headers):
    return requests.post(route, data=data, headers=headers)
