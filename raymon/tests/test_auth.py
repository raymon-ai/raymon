import pytest

import raymon.auth
from raymon.auth import (
    load_m2m_credentials_env,
    save_m2m_config,
    verify_m2m,
    load_m2m_credentials,
    load_m2m_credentials_file,
    save_user_config,
    load_user_credentials,
    verify_user,
)


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
        project_name="testing_project",
        auth_endpoint="http://testing-url",
        audience="test_audience",
        client_id="test_id",
        client_secret="test_secret",
        grant_type="test_grant",
        out=tmp_file,
    )

    config, secret = load_m2m_credentials_file(project_name="testing_project", fpath=tmp_file)
    assert verify_m2m(config, secret)
    assert config["auth_url"] == "http://testing-url"
    assert config["audience"] == "test_audience"
    assert config["client_id"] == "test_id"
    assert config["grant_type"] == "test_grant"
    assert secret == "test_secret"


def test_save_load_secret_multiple(tmp_path):
    tmp_file = tmp_path / "secret.json"
    save_m2m_config(
        project_name="testing_project",
        auth_endpoint="http://testing-url",
        audience="test_audience",
        client_id="test_id",
        client_secret="test_secret",
        grant_type="test_grant",
        out=tmp_file,
    )

    save_m2m_config(
        project_name="testing_project2",
        auth_endpoint="url",
        audience="audience",
        client_id="client_id",
        client_secret="client_secret",
        grant_type="client_credentials",
        out=tmp_file,
    )

    config, secret = load_m2m_credentials_file(project_name="testing_project", fpath=tmp_file)
    assert verify_m2m(config, secret)
    assert config["auth_url"] == "http://testing-url"
    assert config["audience"] == "test_audience"
    assert config["client_id"] == "test_id"
    assert config["grant_type"] == "test_grant"
    assert secret == "test_secret"

    config, secret = load_m2m_credentials_file(project_name="testing_project2", fpath=tmp_file)
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
        project_name="testing_project",
        auth_endpoint="http://testing-url",
        audience="test_audience",
        client_id="test_id",
        client_secret="test_secret",
        grant_type="test_grant",
        out=tmp_file,
    )

    save_m2m_config(
        project_name="testing_project2",
        auth_endpoint="url",
        audience="audience",
        client_id="client_id",
        client_secret="client_secret",
        grant_type="client_credentials",
        out=tmp_file,
    )

    monkeypatch.setenv("RAYMON_AUTH0_URL", "url")
    monkeypatch.setenv("RAYMON_AUDIENCE", "audience")
    monkeypatch.setenv("RAYMON_CLIENT_ID", "client_id")
    monkeypatch.setenv("RAYMON_CLIENT_SECRET_FILE", str(envsecretfile))
    monkeypatch.setenv("RAYMON_GRANT_TYPE", "client_credentials")

    config, secret = load_m2m_credentials(project_name="testing_project", fpath=tmp_file)

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
        project_name="testing_project2",
        auth_endpoint="http://testing-url",
        audience="test_audience",
        client_id="test_id",
        client_secret="test_secret",
        grant_type="test_grant",
        out=no_file,
    )
    with pytest.raises(raymon.auth.SecretError):
        config, secret = load_m2m_credentials(project_name="testing_project", fpath=no_file)


def test_load_waterfall_prio_none():
    with pytest.raises(raymon.auth.SecretError):
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


def test_save_load_secret_multiple(tmp_path):
    tmp_file = tmp_path / "secret.json"
    save_m2m_config(
        project_name="testing_project",
        auth_endpoint="http://testing-url",
        audience="test_audience",
        client_id="test_id",
        client_secret="test_secret",
        grant_type="test_grant",
        out=tmp_file,
    )

    save_m2m_config(
        project_name="testing_project2",
        auth_endpoint="url",
        audience="audience",
        client_id="client_id",
        client_secret="client_secret",
        grant_type="client_credentials",
        out=tmp_file,
    )

    save_user_config(
        auth_endpoint="url",
        audience="audience",
        client_id="client_id",
        out=tmp_file,
    )

    config, secret = load_user_credentials(fpath=tmp_file)
    assert verify_user(config)
    assert config["auth_url"] == "url"
    assert config["audience"] == "audience"
    assert config["client_id"] == "client_id"
    assert secret is None


def test_load_waterfall_user_prio_0(monkeypatch, tmp_path_factory, envsecretfile):

    path1 = tmp_path_factory.mktemp(basename="path1")
    tmp_file = path1 / "secret.json"
    save_user_config(
        auth_endpoint="http://testing-url",
        audience="test_audience",
        client_id="test_id",
        out=tmp_file,
    )

    monkeypatch.setenv("RAYMON_AUTH0_URL", "url")
    monkeypatch.setenv("RAYMON_AUDIENCE", "audience")
    monkeypatch.setenv("RAYMON_CLIENT_ID", "client_id")

    config, secret = load_user_credentials(fpath=tmp_file)

    assert config["auth_url"] == "http://testing-url"
    assert config["audience"] == "test_audience"
    assert config["client_id"] == "test_id"
    assert secret is None


def test_load_waterfall_user_prio_1(monkeypatch):

    monkeypatch.setenv("RAYMON_AUTH0_URL", "url")
    monkeypatch.setenv("RAYMON_AUDIENCE", "audience")
    monkeypatch.setenv("RAYMON_CLIENT_ID", "client_id")

    config, secret = load_user_credentials()

    assert config["auth_url"] == "url"
    assert config["audience"] == "audience"
    assert config["client_id"] == "client_id"
    assert secret is None
