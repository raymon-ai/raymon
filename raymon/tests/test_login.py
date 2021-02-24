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


class DummyreponseNOK:
    ok = False
    text = "Well it failed duh."


def request_token_ok_gen(token):
    def request(*args, **kwargs):
        return DummyTokenreponseOK(token)

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


def test_login_m2m_nok_but_user_ok(monkeypatch, secret_file):
    monkeypatch.setattr(m2m, "login_request", request_nok_gen())
    monkeypatch.setattr(user, "code_request", code_request_ok_gen())
    monkeypatch.setattr(user, "token_request", request_token_ok_gen("user"))

    monkeypatch.setenv("RAYMON_AUTH0_URL", "url")
    monkeypatch.setenv("RAYMON_AUDIENCE", "audience")
    monkeypatch.setenv("RAYMON_CLIENT_ID", "client_id")

    token = login(fpath=secret_file, project_id="testing_project")
    assert token == "user"


def test_login_m2m_nok_user_nok(monkeypatch, secret_file):
    monkeypatch.setattr(m2m, "login_request", request_nok_gen())
    monkeypatch.setattr(user, "code_request", code_request_ok_gen())
    monkeypatch.setattr(user, "token_request", request_nok_gen())

    with pytest.raises(NetworkException):

        _ = login(fpath=secret_file)
