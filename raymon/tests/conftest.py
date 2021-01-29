import pytest
from raymon.auth import save_secret

PROJECT_NAME = "testing_project"


@pytest.fixture
def secret_file(tmp_path):
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
    return tmp_file
