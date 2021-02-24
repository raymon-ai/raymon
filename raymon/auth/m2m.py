from pathlib import Path
import json
import os
import requests
import json
from raymon.exceptions import NetworkException, SecretException

# from raymon.auth import load_credentials_file


def save_m2m_config(
    existing,
    project_name,
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
    project_config = known_configs["m2m"].get(project_name, {})
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


def load_m2m_credentials_env():
    project_config = {}
    project_config["auth_url"] = os.environ["RAYMON_AUTH0_URL"]
    project_config["audience"] = os.environ["RAYMON_AUDIENCE"]
    project_config["client_id"] = os.environ["RAYMON_CLIENT_ID"]
    project_config["grant_type"] = os.environ["RAYMON_GRANT_TYPE"]

    secret = Path(os.environ["RAYMON_CLIENT_SECRET_FILE"]).read_text()
    return verify_m2m(project_config, secret)


def load_m2m_credentials(credentials=None, project_name=None):
    # HIGHEST PRIORITY 0: specified file path
    # Check whether file and project_name are specified, try loading it.
    try:
        assert project_name is not None
        config = credentials.get("m2m")[project_name]["config"]
        secret = credentials.get("m2m")[project_name]["secret"]
        config, secret = verify_m2m(config, secret)
        print(f"Secret loaded from specific file.")
    except Exception as exc:
        print(f"Could not load secret from specific file. ({exc})")
        # PRIORITY 1: ENV Variables
        try:
            config, secret = load_m2m_credentials_env()
            print(f"Secret loaded from env.")
        except Exception as exc:
            print(f"Could not load secret from environment keys. ({exc})")
            raise SecretException(f"Could not load secret for project {project_name}.")

    return config, secret


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
