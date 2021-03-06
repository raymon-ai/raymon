import pytest


from raymon.auth import login
from raymon.auth import m2m
from raymon.auth import user
from raymon.exceptions import NetworkException


class DummyTokenreponseOK:
    def __init__(self, token="token"):
        self.token = token
        self.ok = True

    def json(self):
        return {"access_token": self.token}


class DummyTokenreponseNOK:
    def __init__(self):
        self.ok = False

    def json(self):
        return {"error": "access_denied"}


class DummyreponseNOK:
    ok = False
    text = "Well it failed duh."


def request_token_ok_gen(token):
    def request(*args, **kwargs):
        return DummyTokenreponseOK(token)

    return request


def request_token_nok_gen():
    def request(*args, **kwargs):
        return DummyTokenreponseNOK()

    return request


def request_nok_gen():
    def request(*args, **kwargs):
        return DummyreponseNOK()

    return request


def code_request_ok_gen():
    class CodeReponse:
        def json(self):
            return {"device_code": "42", "interval": 0.1}

    def request(*args, **kwargs):
        return CodeReponse()

    return request


def token_request_ok_gen(token):
    class CodeReponse:
        def json(self):
            return {"device_code": "42", "interval": 0.1}

    def request(*args, **kwargs):
        return CodeReponse()

    return request


def test_login_m2m_ok(monkeypatch, secret_file):
    monkeypatch.setattr(m2m, "login_request", request_token_ok_gen("m2m"))
    token = login(fpath=secret_file, project_id="testing_project")
    assert token == "m2m"


def test_login_m2m_nok_but_user_ok(monkeypatch, secret_file_user):
    monkeypatch.setattr(m2m, "login_request", request_nok_gen())
    monkeypatch.setattr(user, "code_request", code_request_ok_gen())
    monkeypatch.setattr(user, "token_request", request_token_ok_gen("user"))

    token = login(
        fpath=secret_file_user,
        project_id="testing_project",
        env={"auth_url": "testing_auth", "audience": "raymon-backend-api", "client_id": "testing-id"},
    )
    assert token == "user"


def test_login_m2m_nok_user_nok(monkeypatch, secret_file):
    monkeypatch.setattr(m2m, "login_request", request_nok_gen())
    monkeypatch.setattr(user, "code_request", code_request_ok_gen())
    monkeypatch.setattr(user, "token_request", request_token_nok_gen())

    with pytest.raises(NetworkException):
        _ = login(fpath=secret_file)
