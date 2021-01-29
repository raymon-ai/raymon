from pathlib import Path
import json
import os

DEFAULT_FNAME = "~/.raymon/secrets.json"


class SecretError(Exception):
    pass


def save_secret(project_name, auth_endpoint, audience, client_id, client_secret, grant_type, out=DEFAULT_FNAME):
    out = Path(out)

    known_secrets = load_secrets_file(fpath=out)
    # If so, check whether porject exists
    project_secret = known_secrets.get(project_name, {})

    # If exists, overwrite secret
    project_secret["auth_url"] = auth_endpoint
    project_secret["audience"] = audience
    project_secret["client_id"] = client_id
    project_secret["client_secret"] = client_secret
    project_secret["grant_type"] = grant_type

    # Save secret
    known_secrets[project_name] = project_secret
    with open(out, "w") as f:
        json.dump(known_secrets, fp=f, indent=4)


def load_secrets_file(fpath):
    # Check whether outfile exists, load known secrets
    if fpath.is_file():
        known_secrets = json.loads(fpath.read_text())
    else:
        known_secrets = {}
    return known_secrets


def load_secret_file(project_name, fpath):
    known_secrets = load_secrets_file(fpath=Path(fpath))
    project_secret = project_secret = known_secrets[project_name]
    return verify(project_secret)


def load_secret_env():
    project_secret = {}
    project_secret["auth_url"] = os.environ["RAYMON_AUTH0_URL"]
    project_secret["audience"] = os.environ["RAYMON_AUDIENCE"]
    project_secret["client_id"] = os.environ["RAYMON_CLIENT_ID"]
    project_secret["client_secret"] = os.environ["RAYMON_CLIENT_SECRET"]
    project_secret["grant_type"] = os.environ["RAYMON_GRANT_TYPE"]
    return project_secret


def load_secret(project_name=None, fpath=None):
    project_secret = {}
    # HIGHEST PRIORITY 0: specified file path
    # Check whether file and project_name are specified, try loading it.
    try:
        secret = load_secret_file(project_name=project_name, fpath=fpath)
        print(f"Secret loaded from specific file.")
        return secret
    except Exception as exc:
        print(f"Could not load secret from specific file. ({exc})")

    # PRIORITY 1: ENV Variables
    try:
        project_secret = verify(load_secret_env())
        print(f"Secret loaded from env.")
        return project_secret
    except Exception as exc:
        print(f"Could not load secret from environment keys. ({exc})")

    # PRIORITY 2: file in current dir
    try:
        secret = load_secret_file(project_name=project_name, fpath=Path("./.raymon/secrets.json"))
        print(f"Secret loaded from current dir.")
        return secret
    except Exception as exc:
        print(f"Could not load secret from current dir. ({exc})")

    # PRIORITY 3: file in home dir
    try:
        secret = load_secret_file(project_name=project_name, fpath=Path(DEFAULT_FNAME).expanduser())
        print(f"Secret loaded from home dir.")
        return secret
    except Exception as exc:
        print(f"Could not load secret from home dir. ({exc})")

    raise SecretError(f"Could not load secret for project {project_name}.")


def verify(secret):
    keys = ["auth_url", "audience", "client_id", "client_secret", "grant_type"]
    for key in keys:
        assert secret[key] is not None
        assert isinstance(secret[key], str)
    return secret
