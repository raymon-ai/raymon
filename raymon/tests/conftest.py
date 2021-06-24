import pytest

# import raymon
from raymon.auth.m2m import save_m2m_config
from raymon.auth.user import save_user_config
from PIL import Image
import glob

PROJECT_NAME = "testing_project"


@pytest.fixture
def secret_file(tmp_path):
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
    return tmp_file


@pytest.fixture
def secret_file_user(tmp_path):
    tmp_file = tmp_path / "secret.json"
    save_user_config(
        existing={},
        auth_endpoint="http://testing-url",
        audience="test_audience",
        client_id="test_id",
        token=None,
        out=tmp_file,
        env={"auth_url": "testing_auth", "audience": "raymon-backend-api", "client_id": "testing-id"},
    )
    return tmp_file


@pytest.fixture
def envsecretfile(tmp_path):
    tmp_file = tmp_path / "secret.txt"
    with open(tmp_file, "w") as f:
        f.write("client_secret")
    return tmp_file


@pytest.fixture
def images(dpath="raymon/tests/sample_data", lim=10):
    files = glob.glob(dpath + "/*.jpeg")
    images = []
    for n, fpath in enumerate(files):
        if n == lim:
            break
        img = Image.open(fpath)
        img.thumbnail(size=(500, 500))
        images.append(img)
    return images
