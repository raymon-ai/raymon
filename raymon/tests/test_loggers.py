#%%
import pytest
import json
import pendulum
import uuid
from raymon import Trace, RaymonAPI, RaymonAPILogger
from raymon import types as rt
from raymon.tests.conftest import PROJECT_NAME


class Dummyreponse:

    ok = True


tags = [{"name": "my-tag", "value": "my_value", "type": "label", "group": "mygroup"}]


def test_api_logger_info(monkeypatch, secret_file):
    def dummylogin(self):
        pass

    def test_info_post(self, route, json):
        assert route == f"projects/{PROJECT_NAME}/ingest_batch"
        jcr = json[0]
        pendulum.parse(jcr["timestamp"])
        uuid.UUID(jcr["trace_id"], version=4)
        assert jcr["data"] == "This is a test"
        assert jcr["ref"] is None
        assert jcr["project_id"] == PROJECT_NAME
        return Dummyreponse()

    monkeypatch.setattr(RaymonAPI, "login", dummylogin)
    monkeypatch.setattr(RaymonAPI, "post", test_info_post)
    apilogger = RaymonAPILogger(url="willnotbeused", project_id=PROJECT_NAME, auth_path=secret_file, batch_size=1)
    ray = Trace(logger=apilogger)
    ray.info("This is a test")


def test_api_logger_data(monkeypatch, secret_file):
    def dummylogin(self):
        pass

    def test_data_post(self, route, json):
        assert route == f"projects/{PROJECT_NAME}/ingest_batch" ""
        jcr = json[0]
        pendulum.parse(jcr["timestamp"])
        uuid.UUID(jcr["trace_id"], version=4)
        assert jcr["data"]["params"]["data"]["a"] == "b"
        assert jcr["ref"] == "a-test"
        assert jcr["project_id"] == PROJECT_NAME
        return Dummyreponse()

    monkeypatch.setattr(RaymonAPI, "login", dummylogin)
    monkeypatch.setattr(RaymonAPI, "post", test_data_post)
    apilogger = RaymonAPILogger(url="willnotbeused", project_id=PROJECT_NAME, auth_path=secret_file, batch_size=1)
    ray = Trace(logger=apilogger)
    ray.log(ref="a-test", data=rt.Native({"a": "b"}))


def test_api_logger_tags(monkeypatch, secret_file):
    def dummylogin(self):
        pass

    def test_tags_post(self, route, json):
        assert route.startswith(f"projects/{PROJECT_NAME}/ingest_batch")
        # assert route.endswith("/tags")

        jcr = json[0]["data"]
        for tag_orig, tag_log in zip(tags, jcr):

            assert tag_orig["name"] == tag_log["name"]
            assert tag_orig["value"] == tag_log["value"]
            assert tag_orig["type"] == tag_log["type"]
            assert tag_orig["group"] == tag_log["group"]

        return Dummyreponse()

    monkeypatch.setattr(RaymonAPI, "login", dummylogin)
    monkeypatch.setattr(RaymonAPI, "post", test_tags_post)
    apilogger = RaymonAPILogger(url="willnotbeused", project_id=PROJECT_NAME, auth_path=secret_file, batch_size=1)
    ray = Trace(logger=apilogger)
    ray.tag(tags=tags)
