import json
import logging
from logging.handlers import RotatingFileHandler
import sys
from abc import ABC, abstractmethod
import pendulum
import requests
import os
from pathlib import Path
from raymon.auth import login

MB = 1000000


def setup_logger(fname=None, stdout=True):
    # Set up the raymon logger
    logger = logging.getLogger("Raymon")
    if len(logger.handlers) > 0:
        # Already configured
        return logger
    logger.setLevel(logging.DEBUG)
    # Set level to debug -- will use debug messages for binary data
    formatter = logging.Formatter("{asctime} - {name} - {ray_id} - {message}", style="{")

    if fname is not None:
        # Add a file handler
        fh = RotatingFileHandler(fname, maxBytes=100 * MB, backupCount=10)
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)

    if stdout:
        # print(f"Adding stout")
        # Add a stderr handler -- Do not send DEBUG messages to there (will contain binary data)
        sh = logging.StreamHandler(stream=sys.stdout)
        sh.setLevel(logging.INFO)
        sh.setFormatter(formatter)
        logger.addHandler(sh)
    return logger


class RaymonLoggerBase(ABC):
    def __init__(self, project_id="default", auth_path=None):
        self.project_id = project_id
        self.headers = {"Content-type": "application/json"}
        self.token = None
        self.logger = setup_logger(stdout=True)
        self.login(fpath=auth_path)

    def structure(self, ray_id, peephole, data):
        return {
            "timestamp": str(pendulum.now("utc")),
            "ray_id": str(ray_id),
            "peephole": peephole,
            "data": data,
            "project_id": self.project_id,
        }

    @abstractmethod
    def info(self, ray_id, text):
        pass

    @abstractmethod
    def log(self, ray_id, peephole, data):
        pass

    @abstractmethod
    def tag(self, ray_id, tags):
        pass

    """
    Functions related to Authentication
    """

    def login(self, fpath):
        self.token = login(fpath=fpath)
        self.headers["Authorization"] = f"Bearer {self.token}"


class RaymonTextFile(RaymonLoggerBase):
    KB = 1000
    MB = KB * 1000

    def __init__(self, path="/tmp/raymon/", project_id="default", auth_path=None):
        super().__init__(project_id=project_id, auth_path=auth_path)
        self.fname = Path(path) / f"raymon-{os.getpid()}.log"
        self.data_logger = self.setup_datalogger()

    def setup_datalogger(self):
        # Set up the raymon logger
        logger = logging.getLogger("Raymon-data")
        if len(logger.handlers) > 0:
            # Already configured
            return logger
        logger.setLevel(logging.INFO)
        # Add a file handler
        fh = RotatingFileHandler(self.fname, maxBytes=200 * MB, backupCount=10)
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)

        return logger

    def info(self, ray_id, text):
        jcr = self.structure(ray_id=ray_id, peephole=None, data=text)
        kafka_msg = {"type": "info", "jcr": jcr}
        self.logger.info(text, extra=jcr)
        self.data_logger.info(json.dumps(kafka_msg))
        self.logger.info(f"Logged: {text}", extra=jcr)

    def log(self, ray_id, peephole, data):
        jcr = self.structure(ray_id=ray_id, peephole=peephole, data=data.to_jcr())
        kafka_msg = {"type": "data", "jcr": jcr}
        self.logger.info(f"Logging data at {peephole}", extra=jcr)
        self.data_logger.info(json.dumps(kafka_msg))
        self.logger.info(f"Logged peephole {peephole} data to textfile.", extra=jcr)

    def tag(self, ray_id, tags):
        jcr = self.structure(ray_id=ray_id, peephole=None, data=tags)
        kafka_msg = {"type": "tags", "jcr": jcr}
        self.data_logger.info(json.dumps(kafka_msg))
        self.logger.info(f"Logged tags to textfile.", extra=jcr)


class RaymonAPI(RaymonLoggerBase):
    def __init__(self, url="http://localhost:8000", project_id="default", auth_path=None):
        super().__init__(project_id=project_id, auth_path=auth_path)
        self.url = url
        self.session = requests.Session()
        # self.secret = load_secret(project_name=project_id, fpath=secret_fpath)

    """
    Functions related to logging of rays
    """

    def info(self, ray_id, text):
        # print(f"Logging Raymon Datatype...{type(data)}", flush=True)
        jcr = self.structure(ray_id=ray_id, peephole=None, data=text)
        self.logger.info(text, extra=jcr)
        resp = self.post(
            route=f"projects/{self.project_id}/ingest",
            json=jcr,
        )
        status = "OK" if resp.ok else f"ERROR: {resp.status_code}"
        self.logger.info(f"Logged info. Status: {status}", extra=jcr)

    def log(self, ray_id, peephole, data):
        # print(f"Logging Raymon Datatype...{type(data)}", flush=True)
        jcr = self.structure(ray_id=ray_id, peephole=peephole, data=data.to_jcr())
        self.logger.info(f"Logging data at {peephole}", extra=jcr)
        resp = self.post(
            route=f"projects/{self.project_id}/ingest",
            json=jcr,
        )
        status = "OK" if resp.ok else f"ERROR: {resp.status_code}"
        self.logger.info(f"Data logged at {peephole}. Status: {status}", extra=jcr)

    def tag(self, ray_id, tags):
        # TODO validate tags
        jcr = self.structure(ray_id=ray_id, peephole=None, data=tags)
        resp = self.post(
            route=f"projects/{self.project_id}/rays/{ray_id}/tags",
            json=tags,
        )
        status = "OK" if resp.ok else f"ERROR: {resp.status_code}"
        self.logger.info(f"Ray tagged. Status: {status}", extra=jcr)

    """HTTP METHODS"""

    def post(self, route, json, params=None):
        resp = self.session.post(
            f"{self.url}/{route}",
            json=json,
            params=params,
            headers=self.headers,
        )
        return resp

    def put(self, route, json, params=None):
        resp = self.session.put(
            f"{self.url}/{route}",
            json=json,
            params=params,
            headers=self.headers,
        )
        return resp

    def get(self, route, json={}, params=None):
        resp = self.session.get(
            f"{self.url}/{route}",
            json=json,
            params=params,
            headers=self.headers,
        )
        return resp

    def delete(self, route, json={}, params=None):
        resp = self.session.delete(
            f"{self.url}/{route}",
            json=json,
            params=params,
            headers=self.headers,
        )

        return resp

    """API methods"""

    def register_project(self, project_name):
        project_data = {"project_name": project_name}
        resp = self.post(route="projects", json=project_data)
        return resp

    def search_project(self, project_name):
        project_data = {"project_name": project_name}
        resp = self.get(route="projects/search", params=project_data)
        return resp

    def ls_projects(self):
        resp = self.get(route="projects")
        return resp

    def add_org(self, org_id, description):
        org = {"org_id": org_id, "description": description}
        resp = self.post(route="orgs", json=org)
        return resp

    def get_org(self, org_id):
        resp = self.get(route=f"orgs/{org_id}")
        return resp

    def add_user_to_org(self, org_id, user_id, user_readable):
        org = {"user_id": user_id, "user_readable": user_readable}
        resp = self.post(route=f"orgs/{org_id}/users", json=org)
        return resp

    def rm_user_from_org(self, org_id, user_id):
        data = {"user_id": user_id}
        resp = self.delete(route=f"orgs/{org_id}/users", json=data)
        return resp

    def add_m2mclient(self, project_id):
        # org = {"user_id": user_id, "user_readable": user_readable}
        resp = self.post(route=f"projects/{project_id}/m2m", json=None)
        return resp

    def get_m2mclient(self, project_id):
        resp = self.get(route=f"projects/{project_id}/m2m", json=None)
        return resp

    def transfer_project(self, project_id, user_id, org_id):
        # Either user_id or org_id should be None
        owner = {"user_id": user_id, "org_id": org_id}
        resp = self.put(route=f"projects/{project_id}", json=owner)
        return resp
