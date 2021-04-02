from pathlib import Path
import json
import os
import requests
import json
from raymon.exceptions import NetworkException, SecretException

# from raymon.auth import load_credentials_file


def save_m2m_config(
    existing,
    project_id,
    auth_endpoint,
    audience,
    client_id,
    client_secret,
    grant_type,
    out,
):
    out = Path(out)

    known_configs = existing
    # If so, check whether porject exists
    if "m2m" not in known_configs:
        known_configs["m2m"] = {}
    project_config = known_configs["m2m"].get(project_id, {})
    project_config["config"] = {}
    project_config["secret"] = None

    # If exists, overwrite secret
    project_config["config"]["auth_url"] = auth_endpoint
    project_config["config"]["audience"] = audience
    project_config["config"]["client_id"] = client_id
    project_config["secret"] = client_secret
    project_config["config"]["grant_type"] = grant_type

    # Save secret
    known_configs["m2m"][project_id] = project_config
    with open(out, "w") as f:
        json.dump(known_configs, fp=f, indent=4)


def load_m2m_credentials(credentials=None, project_id=None):
    # HIGHEST PRIORITY 0: specified file path
    # Check whether file and project_name are specified, try loading it.

    try:
        assert project_id is not None
        config = credentials.get("m2m")[project_id]["config"]
        secret = credentials.get("m2m")[project_id]["secret"]
        config, secret = verify_m2m(config, secret)
        print(f"M2M secret loaded.")
        return config, secret
    except AssertionError as exc:
        print("Project id is None. Cannot load m2m credentials.")
        raise SecretException from exc
    except Exception as exc:
        print(f"Could not load M2M credentials. {type(exc)}")
        raise SecretException from exc


def verify_m2m(config, secret):
    keys = ["auth_url", "audience", "client_id", "grant_type"]
    for key in keys:
        assert config[key] is not None
        assert isinstance(config[key], str)
    assert isinstance(secret, str)
    return config, secret


def login_m2m_flow(config, secret):
    data = {
        "audience": config["audience"],
        "grant_type": config["grant_type"],
        "client_id": config["client_id"],
        "client_secret": secret,
    }

    route = f"{config['auth_url']}/oauth/token"
    resp = login_request(route, data)
    if not resp.ok:
        raise NetworkException(f"Can not login to Raymon service: \n{resp.text}")
    else:
        token_data = resp.json()
        token = token_data["access_token"]
        return token


def login_request(route, data):
    resp = requests.post(route, data=data)
    return resp
