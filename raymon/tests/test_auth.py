import pytest

import raymon.auth
from raymon.auth import load_secret_env, save_secret, verify, load_secret_file, load_secret


def test_load_env(monkeypatch):
    monkeypatch.setenv("RAYMON_AUTH0_URL", "url")
    monkeypatch.setenv("RAYMON_AUDIENCE", "audience")
    monkeypatch.setenv("RAYMON_CLIENT_ID", "client_id")
    monkeypatch.setenv("RAYMON_CLIENT_SECRET", "client_secret")
    monkeypatch.setenv("RAYMON_GRANT_TYPE", "client_credentials")

    secret = load_secret_env()

    assert secret["auth_url"] == "url"
    assert secret["audience"] == "audience"
    assert secret["client_id"] == "client_id"
    assert secret["client_secret"] == "client_secret"
    assert secret["grant_type"] == "client_credentials"


def test_save_load_secret_single(tmp_path):

    tmp_file = tmp_path / "secret.json"
    save_secret(
        project_name="testing_project",
        auth_endpoint="http://testing-url",
        audience="test_audience",
        client_id="test_id",
        client_secret="test_secret",
        grant_type="test_grant",
        out=tmp_file,
    )

    secret = load_secret_file(project_name="testing_project", fpath=tmp_file)
    assert verify(secret)
    assert secret["auth_url"] == "http://testing-url"
    assert secret["audience"] == "test_audience"
    assert secret["client_id"] == "test_id"
    assert secret["client_secret"] == "test_secret"
    assert secret["grant_type"] == "test_grant"


def test_save_load_secret_multiple(tmp_path):
    tmp_file = tmp_path / "secret.json"
    save_secret(
        project_name="testing_project",
        auth_endpoint="http://testing-url",
        audience="test_audience",
        client_id="test_id",
        client_secret="test_secret",
        grant_type="test_grant",
        out=tmp_file,
    )

    save_secret(
        project_name="testing_project2",
        auth_endpoint="url",
        audience="audience",
        client_id="client_id",
        client_secret="client_secret",
        grant_type="client_credentials",
        out=tmp_file,
    )

    secret = load_secret_file(project_name="testing_project", fpath=tmp_file)
    assert verify(secret)
    assert secret["auth_url"] == "http://testing-url"
    assert secret["audience"] == "test_audience"
    assert secret["client_id"] == "test_id"
    assert secret["client_secret"] == "test_secret"
    assert secret["grant_type"] == "test_grant"

    secret = load_secret_file(project_name="testing_project2", fpath=tmp_file)
    assert verify(secret)
    assert secret["auth_url"] == "url"
    assert secret["audience"] == "audience"
    assert secret["client_id"] == "client_id"
    assert secret["client_secret"] == "client_secret"
    assert secret["grant_type"] == "client_credentials"


def test_load_waterfall_prio_0(monkeypatch, tmp_path_factory):

    path1 = tmp_path_factory.mktemp(basename="path1")
    tmp_file = path1 / "secret.json"
    save_secret(
        project_name="testing_project",
        auth_endpoint="http://testing-url",
        audience="test_audience",
        client_id="test_id",
        client_secret="test_secret",
        grant_type="test_grant",
        out=tmp_file,
    )

    save_secret(
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
    monkeypatch.setenv("RAYMON_CLIENT_SECRET", "client_secret")
    monkeypatch.setenv("RAYMON_GRANT_TYPE", "client_credentials")

    secret = load_secret(project_name="testing_project", fpath=tmp_file)

    assert secret["auth_url"] == "http://testing-url"
    assert secret["audience"] == "test_audience"
    assert secret["client_id"] == "test_id"
    assert secret["client_secret"] == "test_secret"
    assert secret["grant_type"] == "test_grant"


def test_load_waterfall_prio_1(monkeypatch, tmp_path_factory):

    # path1 = tmp_path_factory.mktemp()
    # path2 = tmp_path_factory.mktemp()

    monkeypatch.setenv("RAYMON_AUTH0_URL", "url")
    monkeypatch.setenv("RAYMON_AUDIENCE", "audience")
    monkeypatch.setenv("RAYMON_CLIENT_ID", "client_id")
    monkeypatch.setenv("RAYMON_CLIENT_SECRET", "client_secret")
    monkeypatch.setenv("RAYMON_GRANT_TYPE", "client_credentials")

    secret = load_secret()

    assert secret["auth_url"] == "url"
    assert secret["audience"] == "audience"
    assert secret["client_id"] == "client_id"
    assert secret["client_secret"] == "client_secret"
    assert secret["grant_type"] == "client_credentials"


def test_load_waterfall_prio_3(monkeypatch, tmp_path_factory):

    path1 = tmp_path_factory.mktemp(basename="path1")
    path2 = tmp_path_factory.mktemp(basename="path2")
    no_file = path1 / "secret.json"
    tmp_file = path2 / "secret.json"

    save_secret(
        project_name="testing_project",
        auth_endpoint="http://testing-url",
        audience="test_audience",
        client_id="test_id",
        client_secret="test_secret",
        grant_type="test_grant",
        out=tmp_file,
    )
    monkeypatch.setattr(raymon.auth, "DEFAULT_FNAME", tmp_file)
    assert raymon.auth.DEFAULT_FNAME == tmp_file

    secret = load_secret(project_name="testing_project", fpath=no_file)

    assert secret["auth_url"] == "http://testing-url"
    assert secret["audience"] == "test_audience"
    assert secret["client_id"] == "test_id"
    assert secret["client_secret"] == "test_secret"
    assert secret["grant_type"] == "test_grant"


def test_load_waterfall_prio_none():
    with pytest.raises(raymon.auth.SecretError):
        _ = load_secret()


def test_verify():

    secret_good = {
        "auth_url": "url",
        "audience": "audience",
        "client_id": "client_id",
        "client_secret": "client_secret",
        "grant_type": "client_credentials",
    }
    assert verify(secret_good)

    secret_bad1 = {
        "audience": "audience",
        "client_id": "client_id",
        "client_secret": "client_secret",
        "grant_type": "client_credentials",
    }
    try:
        verify(secret_bad1)
        pytest.fail("Expected Failure on auth_url key")
    except:
        pass

    secret_bad2 = {
        "auth_url": "url",
        "audience": "audience",
        "client_id": "client_id",
        "grant_type": "client_credentials",
    }
    try:
        verify(secret_bad2)
        pytest.fail("Expected Failure on client_secret key")
    except:
        pass
