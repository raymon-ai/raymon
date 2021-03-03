import pytest
import pendulum
import base64
import json
import raymon

from raymon.auth import load_credentials_file
from raymon.auth.m2m import (
    load_m2m_credentials_env,
    save_m2m_config,
    verify_m2m,
    load_m2m_credentials,
)

from raymon.auth.user import (
    save_user_config,
    load_user_credentials,
    verify_user,
    token_ok,
)
from raymon.exceptions import SecretException


def test_load_env(monkeypatch, envsecretfile):
    monkeypatch.setenv("RAYMON_AUTH0_URL", "url")
    monkeypatch.setenv("RAYMON_AUDIENCE", "audience")
    monkeypatch.setenv("RAYMON_CLIENT_ID", "client_id")
    monkeypatch.setenv("RAYMON_CLIENT_SECRET_FILE", str(envsecretfile))
    monkeypatch.setenv("RAYMON_GRANT_TYPE", "client_credentials")

    config, secret = load_m2m_credentials_env()

    assert config["auth_url"] == "url"
    assert config["audience"] == "audience"
    assert config["client_id"] == "client_id"
    assert config["grant_type"] == "client_credentials"
    assert secret == "client_secret"


def test_save_load_secret_single(tmp_path):

    tmp_file = tmp_path / "secret.json"
    save_m2m_config(
        existing={},
        project_id="testing_project",
        auth_endpoint="http://testing-url",
        audience="test_audience",
        client_id="test_id",
        client_secret="test_secret",
        grant_type="test_grant",
        out=tmp_file,
    )
    credentials = load_credentials_file(fpath=tmp_file)
    config, secret = load_m2m_credentials(credentials=credentials, project_id="testing_project")
    assert verify_m2m(config, secret)
    assert config["auth_url"] == "http://testing-url"
    assert config["audience"] == "test_audience"
    assert config["client_id"] == "test_id"
    assert config["grant_type"] == "test_grant"
    assert secret == "test_secret"


def test_save_load_secret_multiple(tmp_path):
    tmp_file = tmp_path / "secret.json"
    save_m2m_config(
        existing={},
        project_id="testing_project",
        auth_endpoint="http://testing-url",
        audience="test_audience",
        client_id="test_id",
        client_secret="test_secret",
        grant_type="test_grant",
        out=tmp_file,
    )
    existing = load_credentials_file(tmp_file)
    save_m2m_config(
        existing=existing,
        project_id="testing_project2",
        auth_endpoint="url",
        audience="audience",
        client_id="client_id",
        client_secret="client_secret",
        grant_type="client_credentials",
        out=tmp_file,
    )
    credentials = load_credentials_file(fpath=tmp_file)
    config, secret = load_m2m_credentials(credentials=credentials, project_id="testing_project")
    assert verify_m2m(config, secret)
    assert config["auth_url"] == "http://testing-url"
    assert config["audience"] == "test_audience"
    assert config["client_id"] == "test_id"
    assert config["grant_type"] == "test_grant"
    assert secret == "test_secret"

    config, secret = load_m2m_credentials(credentials=credentials, project_id="testing_project2")
    assert verify_m2m(config, secret)
    assert config["auth_url"] == "url"
    assert config["audience"] == "audience"
    assert config["client_id"] == "client_id"
    assert config["grant_type"] == "client_credentials"
    assert secret == "client_secret"


def test_load_waterfall_prio_0(monkeypatch, tmp_path_factory, envsecretfile):

    path1 = tmp_path_factory.mktemp(basename="path1")
    tmp_file = path1 / "secret.json"
    save_m2m_config(
        existing={},
        project_id="testing_project",
        auth_endpoint="http://testing-url",
        audience="test_audience",
        client_id="test_id",
        client_secret="test_secret",
        grant_type="test_grant",
        out=tmp_file,
    )
    existing = load_credentials_file(tmp_file)
    save_m2m_config(
        existing=existing,
        project_id="testing_project2",
        auth_endpoint="url",
        audience="audience",
        client_id="client_id",
        client_secret="client_secret",
        grant_type="client_credentials",
        out=tmp_file,
    )

    monkeypatch.setenv("RAYMON_AUTH0_URL", "url-env")
    monkeypatch.setenv("RAYMON_AUDIENCE", "audience-env")
    monkeypatch.setenv("RAYMON_CLIENT_ID", "client_id-env")
    monkeypatch.setenv("RAYMON_CLIENT_SECRET_FILE", str(envsecretfile))
    monkeypatch.setenv("RAYMON_GRANT_TYPE", "client_credentials-env")

    credentials = load_credentials_file(fpath=tmp_file)
    config, secret = load_m2m_credentials(credentials=credentials, project_id="testing_project")

    assert config["auth_url"] == "http://testing-url"
    assert config["audience"] == "test_audience"
    assert config["client_id"] == "test_id"
    assert secret == "test_secret"
    assert config["grant_type"] == "test_grant"


def test_load_waterfall_prio_1(monkeypatch, tmp_path_factory, envsecretfile):

    # path1 = tmp_path_factory.mktemp()
    # path2 = tmp_path_factory.mktemp()

    monkeypatch.setenv("RAYMON_AUTH0_URL", "url")
    monkeypatch.setenv("RAYMON_AUDIENCE", "audience")
    monkeypatch.setenv("RAYMON_CLIENT_ID", "client_id")
    monkeypatch.setenv("RAYMON_CLIENT_SECRET_FILE", str(envsecretfile))
    monkeypatch.setenv("RAYMON_GRANT_TYPE", "client_credentials")

    config, secret = load_m2m_credentials()

    assert config["auth_url"] == "url"
    assert config["audience"] == "audience"
    assert config["client_id"] == "client_id"
    assert secret == "client_secret"
    assert config["grant_type"] == "client_credentials"


def test_load_waterfall_prio_3(monkeypatch, tmp_path_factory):

    path1 = tmp_path_factory.mktemp(basename="path1")
    no_file = path1 / "secret.json"

    save_m2m_config(
        existing={},
        project_id="testing_project2",
        auth_endpoint="http://testing-url",
        audience="test_audience",
        client_id="test_id",
        client_secret="test_secret",
        grant_type="test_grant",
        out=no_file,
    )
    with pytest.raises(SecretException):
        config, secret = load_m2m_credentials(project_id="testing_project")


def test_load_waterfall_prio_none():
    with pytest.raises(SecretException):
        _ = load_m2m_credentials()


def test_verify_m2m():
    secret_good = "client_secret"

    config_good = {
        "auth_url": "url",
        "audience": "audience",
        "client_id": "client_id",
        "grant_type": "client_credentials",
    }
    assert verify_m2m(config_good, secret_good)

    config_bad1 = {
        "audience": "audience",
        "client_id": "client_id",
        "grant_type": "client_credentials",
    }
    try:
        verify_m2m(config_bad1, secret_good)
        pytest.fail("Expected Failure on auth_url key")
    except:
        pass

    config_bad2 = {
        "auth_url": "url",
        "audience": "audience",
        "client_id": "client_id",
    }
    try:
        verify_m2m(config_bad2, secret_good)
        pytest.fail("Expected Failure on grant_type key")
    except:
        pass


def test_save_load_secret_multiple_with_user(tmp_path):
    tmp_file = tmp_path / "secret.json"
    save_m2m_config(
        existing={},
        project_id="testing_project",
        auth_endpoint="http://testing-url",
        audience="test_audience",
        client_id="test_id",
        client_secret="test_secret",
        grant_type="test_grant",
        out=tmp_file,
    )
    existing = load_credentials_file(tmp_file)
    save_m2m_config(
        existing=existing,
        project_id="testing_project2",
        auth_endpoint="url",
        audience="audience",
        client_id="client_id",
        client_secret="client_secret",
        grant_type="client_credentials",
        out=tmp_file,
    )
    existing = load_credentials_file(tmp_file)
    save_user_config(
        existing=existing,
        auth_endpoint="url",
        audience="audience",
        client_id="client_id",
        token=None,
        out=tmp_file,
    )
    credentials = load_credentials_file(fpath=tmp_file)
    config, secret = load_user_credentials(credentials=credentials)
    assert verify_user(config)
    assert config["auth_url"] == "url"
    assert config["audience"] == "audience"
    assert config["client_id"] == "client_id"
    assert secret is None


def test_load_waterfall_user_prio_0(monkeypatch, tmp_path_factory, envsecretfile):

    path1 = tmp_path_factory.mktemp(basename="path1")
    tmp_file = path1 / "secret.json"
    save_user_config(
        existing={},
        auth_endpoint="http://testing-url",
        audience="test_audience",
        client_id="test_id",
        token=None,
        out=tmp_file,
    )

    monkeypatch.setenv("RAYMON_AUTH0_URL", "url")
    monkeypatch.setenv("RAYMON_AUDIENCE", "audience")
    monkeypatch.setenv("RAYMON_CLIENT_ID", "client_id")

    credentials = load_credentials_file(fpath=tmp_file)
    config, secret = load_user_credentials(credentials=credentials)

    assert config["auth_url"] == "http://testing-url"
    assert config["audience"] == "test_audience"
    assert config["client_id"] == "test_id"
    assert secret is None


def test_load_waterfall_user_prio_1(monkeypatch, tmp_path_factory):

    monkeypatch.setenv("RAYMON_AUTH0_URL", "url")
    monkeypatch.setenv("RAYMON_AUDIENCE", "audience")
    monkeypatch.setenv("RAYMON_CLIENT_ID", "client_id")

    path1 = tmp_path_factory.mktemp(basename="path1")
    no_file = path1 / "secret.json"

    monkeypatch.setattr(raymon.auth, "DEFAULT_FNAME", no_file)
    assert raymon.auth.DEFAULT_FNAME == no_file
    credentials = load_credentials_file(fpath=no_file)

    config, secret = load_user_credentials(credentials=credentials)

    assert config["auth_url"] == "url"
    assert config["audience"] == "audience"
    assert config["client_id"] == "client_id"
    assert secret is None


def test_load_waterfall_user_prio_none(monkeypatch, tmp_path_factory):
    path1 = tmp_path_factory.mktemp(basename="path1")
    no_file = path1 / "secret.json"

    monkeypatch.setattr(raymon.auth, "DEFAULT_FNAME", no_file)
    assert raymon.auth.DEFAULT_FNAME == no_file
    credentials = load_credentials_file(fpath=no_file)

    with pytest.raises(SecretException):
        _ = load_user_credentials(credentials=credentials)


def test_token_ok():
    claims = json.dumps({"exp": int(pendulum.now().add(hours=2, minutes=-1).timestamp())})
    claims = base64.b64encode(claims.encode()).decode()
    token = f"header.{claims}.sign"
    assert not token_ok(token)

    claims = json.dumps({"exp": int(pendulum.now().add(minutes=-1).timestamp())})
    claims = base64.b64encode(claims.encode()).decode()
    token = f"header.{claims}.sign"
    assert not token_ok(token)

    claims = json.dumps({"exp": int(pendulum.now().add(hours=2, minutes=1).timestamp())})
    claims = base64.b64encode(claims.encode()).decode()
    token = f"header.{claims}.sign"
    assert token_ok(token)
