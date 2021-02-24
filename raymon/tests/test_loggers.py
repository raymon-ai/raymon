#%%
import pytest
import json
import pendulum
import uuid
from raymon import Ray, RaymonAPI, RaymonTextFile
from raymon import types as rt
from raymon.tests.conftest import PROJECT_NAME


class Dummyreponse:

    ok = True


tags = [{"name": "my-tag", "value": "my_value", "type": "label", "group": "mygroup"}]


def test_textfile(tmp_path, monkeypatch, secret_file):
    def dummylogin(self, fpath):
        pass

    monkeypatch.setattr(RaymonTextFile, "login", dummylogin)

    fpath = tmp_path
    logger = RaymonTextFile(path=fpath, project_id=PROJECT_NAME)
    ray = Ray(logger=logger)
    ray.info("This is a test")
    ray.log(peephole="a-test", data=rt.Native({"a": "b"}))
    ray.tag(tags=tags)

    # load log file
    with open(logger.fname, "r") as f:
        lines = f.readlines()

    # First line --info
    """
    {"type": "info", "jcr": {"timestamp": "2021-01-29T08:33:51.428387+00:00", "ray_id": "3cc9dec5-e9e5-48b4-8c5c-ba2b48460c92", "peephole": null, "data": "This is a test", "project_id": "testing"}}
    """
    line = json.loads(lines[0])
    assert line["type"] == "info"
    jcr = line["jcr"]
    # No error should be raised when parsing timestamp str
    pendulum.parse(jcr["timestamp"])
    uuid.UUID(jcr["ray_id"], version=4)
    assert jcr["data"] == "This is a test"
    assert jcr["peephole"] is None
    assert jcr["project_id"] == PROJECT_NAME

    # 2nd line --data
    """
    {"type": "info", "jcr": {"timestamp": "2021-01-29T08:33:51.428387+00:00", "ray_id": "3cc9dec5-e9e5-48b4-8c5c-ba2b48460c92", "peephole": null, "data": "This is a test", "project_id": "testing"}}
    """
    line = json.loads(lines[1])
    assert line["type"] == "data"
    jcr = line["jcr"]
    # No error should be raised when parsing timestamp str
    pendulum.parse(jcr["timestamp"])
    uuid.UUID(jcr["ray_id"], version=4)
    assert jcr["data"]["params"]["data"]["a"] == "b"
    assert jcr["peephole"] == "a-test"
    assert jcr["project_id"] == PROJECT_NAME

    # 3rd line --tags
    """
    {"type": "tags", "jcr": {"timestamp": "2021-01-29T08:33:51.473413+00:00", "ray_id": "3cc9dec5-e9e5-48b4-8c5c-ba2b48460c92", "peephole": null, "data": [{"name": "my-tag", "value": "my_value", "type": "label", "group": "mygroup"}], "project_id": "testing"}}
    """
    line = json.loads(lines[2])
    assert line["type"] == "tags"
    jcr = line["jcr"]
    # No error should be raised when parsing timestamp str
    pendulum.parse(jcr["timestamp"])
    uuid.UUID(jcr["ray_id"], version=4)
    for tag_orig, tag_log in zip(tags, jcr["data"]):
        assert tag_orig["name"] == tag_log["name"]
        assert tag_orig["value"] == tag_log["value"]
        assert tag_orig["type"] == tag_log["type"]
        assert tag_orig["group"] == tag_log["group"]

    assert jcr["peephole"] is None
    assert jcr["project_id"] == PROJECT_NAME


def test_api_logger_info(monkeypatch, secret_file):
    def dummylogin(self, fpath):
        pass

    def test_info_post(self, route, data):
        assert route == f"willnotbeused/projects/{PROJECT_NAME}/ingest"
        jcr = data
        pendulum.parse(jcr["timestamp"])
        uuid.UUID(jcr["ray_id"], version=4)
        assert jcr["data"] == "This is a test"
        assert jcr["peephole"] is None
        assert jcr["project_id"] == PROJECT_NAME
        return Dummyreponse()

    monkeypatch.setattr(RaymonAPI, "login", dummylogin)
    monkeypatch.setattr(RaymonAPI, "post", test_info_post)
    apilogger = RaymonAPI(url="willnotbeused", project_id=PROJECT_NAME, auth_path=secret_file)
    ray = Ray(logger=apilogger)
    ray.info("This is a test")


def test_api_logger_data(monkeypatch, secret_file):
    def dummylogin(self, fpath):
        pass

    def test_data_post(self, route, data):
        assert route == f"willnotbeused/projects/{PROJECT_NAME}/ingest" ""
        jcr = data
        pendulum.parse(jcr["timestamp"])
        uuid.UUID(jcr["ray_id"], version=4)
        assert jcr["data"]["params"]["data"]["a"] == "b"
        assert jcr["peephole"] == "a-test"
        assert jcr["project_id"] == PROJECT_NAME
        return Dummyreponse()

    monkeypatch.setattr(RaymonAPI, "login", dummylogin)
    monkeypatch.setattr(RaymonAPI, "post", test_data_post)
    apilogger = RaymonAPI(url="willnotbeused", project_id=PROJECT_NAME, auth_path=secret_file)
    ray = Ray(logger=apilogger)
    ray.log(peephole="a-test", data=rt.Native({"a": "b"}))


def test_api_logger_tags(monkeypatch, secret_file):
    def dummylogin(self, fpath):
        pass

    def test_tags_post(self, route, data):
        assert route.startswith(f"willnotbeused/projects/{PROJECT_NAME}/rays")
        assert route.endswith("/tags")
        jcr = data
        for tag_orig, tag_log in zip(tags, jcr):
            assert tag_orig["name"] == tag_log["name"]
            assert tag_orig["value"] == tag_log["value"]
            assert tag_orig["type"] == tag_log["type"]
            assert tag_orig["group"] == tag_log["group"]

        return Dummyreponse()

    monkeypatch.setattr(RaymonAPI, "login", dummylogin)
    monkeypatch.setattr(RaymonAPI, "post", test_tags_post)
    apilogger = RaymonAPI(url="willnotbeused", project_id=PROJECT_NAME, auth_path=secret_file)
    ray = Ray(logger=apilogger)
    ray.tag(tags=tags)
