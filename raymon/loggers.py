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

    @abstractmethod
    def flush(self):
        pass

    """
    Functions related to Authentication
    """

    def login(self, fpath):
        self.token = login(fpath=fpath)
        self.headers["Authorization"] = f"Bearer {self.token}"


class RaymonAPI(RaymonLoggerBase):
    def __init__(self, url="http://localhost:8000", project_id="default", auth_path=None):
        super().__init__(project_id=project_id, auth_path=auth_path)
        self.url = url
        # self.secret = load_secret(project_name=project_id, fpath=secret_fpath)

    """
    Functions related to logging of rays
    """

    def info(self, ray_id, text):
        # print(f"Logging Raymon Datatype...{type(data)}", flush=True)
        jcr = self.structure(ray_id=ray_id, peephole=None, data=text)
        self.logger.info(text, extra=jcr)
        resp = self.post(route=f"{self.url}/projects/{self.project_id}/ingest", data=jcr)
        status = "OK" if resp.ok else f"ERROR: {resp.status_code}"
        self.logger.info(f"Logged info. Status: {status}", extra=jcr)

    def log(self, ray_id, peephole, data):
        # print(f"Logging Raymon Datatype...{type(data)}", flush=True)
        jcr = self.structure(ray_id=ray_id, peephole=peephole, data=data.to_jcr())
        self.logger.info(f"Logging data at {peephole}", extra=jcr)
        resp = self.post(route=f"{self.url}/projects/{self.project_id}/ingest", data=jcr)
        status = "OK" if resp.ok else f"ERROR: {resp.status_code}"
        self.logger.info(f"Data logged at {peephole}. Status: {status}", extra=jcr)

    def tag(self, ray_id, tags):
        # TODO validate tags
        jcr = self.structure(ray_id=ray_id, peephole=None, data=tags)
        resp = self.post(route=f"{self.url}/projects/{self.project_id}/rays/{ray_id}/tags", data=tags)
        status = "OK" if resp.ok else f"ERROR: {resp.status_code}"
        self.logger.info(f"Ray tagged. Status: {status}", extra=jcr)

    def post(self, route, data):
        resp = requests.post(f"{self.url}/{route}", json=data, headers=self.headers)
        return resp

    def get(self, route, params):
        resp = requests.get(f"{self.url}/{route}", params=params, headers=self.headers)

        return resp

    def flush(self):
        # We don't need to do anything here
        pass


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
        # print(f"Logging Raymon Datatype...{type(data)}", flush=True)
        jcr = self.structure(ray_id=ray_id, peephole=None, data=text)
        kafka_msg = {"type": "info", "jcr": jcr}
        self.logger.info(text, extra=jcr)
        self.data_logger.info(json.dumps(kafka_msg))
        self.logger.info(f"Logged: {text}", extra=jcr)

    def log(self, ray_id, peephole, data):
        # print(f"Logging Raymon Datatype...{type(data)}", flush=True)
        jcr = self.structure(ray_id=ray_id, peephole=peephole, data=data.to_jcr())
        kafka_msg = {"type": "data", "jcr": jcr}
        self.logger.info(f"Logging data at {peephole}", extra=jcr)
        # resp = requests.post(f"{self.url}/projects/{self.project_id}/ingest", json=jcr, headers=self.headers)
        self.data_logger.info(json.dumps(kafka_msg))
        self.logger.info(f"Logged peephole {peephole} data to textfile.", extra=jcr)

    def tag(self, ray_id, tags):
        # TODO validate tags
        jcr = self.structure(ray_id=ray_id, peephole=None, data=tags)
        kafka_msg = {"type": "tags", "jcr": jcr}
        # resp = requests.post(f"{self.url}/projects/{self.project_id}/rays/{ray_id}/tags", json=tags, headers=self.headers)
        self.data_logger.info(json.dumps(kafka_msg))
        self.logger.info(f"Logged tags to textfile.", extra=jcr)

    def flush(self):
        # We don't need to do anything here
        pass
