from pathlib import Path
import json
import os
import requests
import time
import json
import pendulum
from raymon.exceptions import NetworkException
import base64

DEFAULT_FNAME = "~/.raymon/secrets.json"


class SecretError(Exception):
    pass


def save_m2m_config(project_name, auth_endpoint, audience, client_id, client_secret, grant_type, out=DEFAULT_FNAME):
    out = Path(out)

    known_configs = load_credentials_file(fpath=out)
    # If so, check whether porject exists
    project_config = known_configs.get("m2m", {}).get(project_name, {})
    project_config["config"] = {}
    project_config["secret"] = None

    # If exists, overwrite secret
    project_config["config"]["auth_url"] = auth_endpoint
    project_config["config"]["audience"] = audience
    project_config["config"]["client_id"] = client_id
    project_config["secret"] = client_secret
    project_config["config"]["grant_type"] = grant_type

    # Save secret
    known_configs["m2m"][project_name] = project_config
    with open(out, "w") as f:
        json.dump(known_configs, fp=f, indent=4)


def save_user_config(auth_endpoint, audience, client_id, token=None, out=DEFAULT_FNAME):
    out = Path(out)

    known_configs = load_credentials_file(fpath=out)
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


def load_credentials_file(fpath):
    # Check whether outfile exists, load known secrets
    if fpath.is_file():
        known_secrets = json.loads(fpath.read_text())
    else:
        known_secrets = {"user": {}, "m2m": {}}
    return known_secrets


def load_m2m_credentials_file(project_name, fpath):
    known_secrets = load_credentials_file(fpath=Path(fpath))
    config = known_secrets.get("m2m")[project_name]["config"]
    secret = known_secrets.get("m2m")[project_name]["secret"]
    return verify_m2m(config, secret)


def load_user_credentials_file(fpath):
    known_secrets = load_credentials_file(fpath=Path(fpath))
    token = known_secrets.get("user", {}).get("secret", None)
    config = known_secrets.get("user", {}).get("config", {})
    return verify_user(config), token


def load_m2m_credentials_env():
    project_config = {}
    project_config["auth_url"] = os.environ["RAYMON_AUTH0_URL"]
    project_config["audience"] = os.environ["RAYMON_AUDIENCE"]
    project_config["client_id"] = os.environ["RAYMON_CLIENT_ID"]
    project_config["grant_type"] = os.environ["RAYMON_GRANT_TYPE"]

    secret = Path(os.environ["RAYMON_CLIENT_SECRET_FILE"]).read_text()
    return verify_m2m(project_config, secret)


def load_m2m_credentials(project_name=None, fpath=None):
    project_secret = {}
    # HIGHEST PRIORITY 0: specified file path
    # Check whether file and project_name are specified, try loading it.
    try:
        config, secret = load_m2m_credentials_file(project_name=project_name, fpath=fpath)
        print(f"Secret loaded from specific file.")
    except Exception as exc:
        print(f"Could not load secret from specific file. ({exc})")
        # PRIORITY 1: ENV Variables
        try:
            config, secret = load_m2m_credentials_env()
            print(f"Secret loaded from env.")
        except Exception as exc:
            print(f"Could not load secret from environment keys. ({exc})")
            raise SecretError(f"Could not load secret for project {project_name}.")

    return config, secret


def verify_m2m(config, secret):
    keys = ["auth_url", "audience", "client_id", "grant_type"]
    for key in keys:
        assert config[key] is not None
        assert isinstance(config[key], str)
    assert isinstance(secret, str)
    return config, secret


def load_user_credentials(fpath=None):

    # HIGHEST PRIORITY 0: specified file path
    # Check whether file and project_name are specified, try loading it.
    try:
        config, secret = load_user_credentials_file(fpath=fpath)
        print(f"Secret loaded from specific file.")
        return config, secret
    except Exception as exc:
        print(f"Could not load token or config from specific file. ({exc})")

    # PRIORITY 1: ENV Variables
    try:
        secret = None
        config = verify_user(load_user_credentials_env())
        print(f"Secret loaded from env.")
        return config, secret
    except Exception as exc:
        print(f"Could not load config from environment keys. ({exc})")

    raise SecretError(f"Could not load login config.")


def verify_user(config):
    keys = ["auth_url", "audience", "client_id"]
    for key in keys:
        assert config[key] is not None
        assert isinstance(config[key], str)
    return config


def load_user_credentials_env():
    project_config = {}
    project_config["auth_url"] = os.environ["RAYMON_AUTH0_URL"]
    project_config["audience"] = os.environ["RAYMON_AUDIENCE"]
    project_config["client_id"] = os.environ["RAYMON_CLIENT_ID"]
    return verify_user(project_config)


def login_m2m_flow(config, secret):
    data = {
        "audience": config["audience"],
        "grant_type": config["grant_type"],
        "client_id": config["client_id"],
        "client_secret": secret,
    }

    route = f"{config['auth_url']}/oauth/token"
    resp = requests.post(route, data=data)
    if resp.status_code != 200:
        raise NetworkException(f"Can not login to Raymon service: \n{resp.text}")
    else:
        token_data = resp.json()
        token = token_data["access_token"]
        return token


def login_device_flow(config):
    data = dict(client_id=config["client_id"], audience=config["audience"], scope="")
    auth_url = config["auth_url"]
    headers = {"content-type": "application/x-www-form-urlencoded"}
    resp = requests.post(f"{auth_url}/oauth/device/code", data=data, headers=headers)
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
        resp = requests.post(f"{auth_url}/oauth/token", data=data, headers=headers)

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


def token_ok(token):
    claims = json.loads(base64.b64decode(token.split(".")[1] + "===").decode())
    expires = pendulum.from_timestamp(claims["exp"])
    ttl = expires - pendulum.now()
    print(ttl)
    if ttl.hours < 0:
        print(f"Token expired")
        return False
    elif ttl.hours < 2:
        print("Token about to expire.")
        return False
    else:
        print("Token OK")
        return True
