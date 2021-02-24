import pytest

# import raymon
from raymon.auth.m2m import save_m2m_config

PROJECT_NAME = "testing_project"


@pytest.fixture
def secret_file(tmp_path):
    tmp_file = tmp_path / "secret.json"
    save_m2m_config(
        existing={},
        project_name="testing_project",
        auth_endpoint="http://testing-url",
        audience="test_audience",
        client_id="test_id",
        client_secret="test_secret",
        grant_type="test_grant",
        out=tmp_file,
    )
    return tmp_file


@pytest.fixture
def envsecretfile(tmp_path):
    tmp_file = tmp_path / "secret.txt"
    with open(tmp_file, "w") as f:
        f.write("client_secret")
    return tmp_file
