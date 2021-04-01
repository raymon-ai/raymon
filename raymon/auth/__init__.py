import json
from pathlib import Path
from raymon.auth.m2m import (
    load_m2m_credentials,
    login_m2m_flow,
)
from raymon.auth.user import (
    load_user_credentials,
    login_device_flow,
    token_ok,
    save_user_config,
)
from raymon.exceptions import NetworkException, SecretException

DEFAULT_FNAME = Path("~/.raymon/secrets.json").expanduser().absolute()


def load_credentials_file(fpath):
    # Check whether outfile exists, load known secrets
    print(f"Trying to load credentials from {fpath}...", end=" ")
    try:
        known_secrets = json.loads(fpath.read_text())
    except FileNotFoundError:
        known_secrets = {
            "user": {},
            "m2m": {},
        }
    print("Done.")
    return known_secrets


def login_m2m(credentials, project_id):
    config, secret = load_m2m_credentials(credentials=credentials, project_id=project_id)
    return login_m2m_flow(config=config, secret=secret)


def login_user(credentials, out, env):
    config, token = load_user_credentials(credentials=credentials, env=env)
    # check token valid?
    if not token_ok(token):
        token = login_device_flow(config)
    save_user_config(
        existing=credentials,
        auth_endpoint=config["auth_url"],
        audience=config["audience"],
        client_id=config["client_id"],
        token=token,
        out=out,
        env=env,
    )
    return token


def login(fpath, project_id=None, env=None):
    token = None
    if fpath is None:
        fpath = DEFAULT_FNAME
    if env is None:
        env = {
            "auth_url": "https://raymon.eu.auth0.com",
            "audience": "raymon-backend-api",
            "client_id": "h6L3zj5d9OOQK2m0fHMfdFOnNn4LM7gK",
        }
    credentials = load_credentials_file(fpath=fpath)
    # See whether we have m2m credentials set
    try:
        token = login_m2m(credentials=credentials, project_id=project_id)
        return token
    except (SecretException, NetworkException):
        print(f"Could not login with m2m credentials. Trying user credentials.")
    # If we did not find m2m credentials, let the user login interactively.
    try:
        token = login_user(credentials=credentials, out=fpath, env=env)
    except (SecretException, NetworkException) as exc:
        print(f"Could not login with user credentials.")

    if token is None:
        raise NetworkException("Could not login user or machine.")
    return token
