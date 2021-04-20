import json
import uuid
import logging
from logging.handlers import RotatingFileHandler
import sys
from abc import ABC, abstractmethod
import pendulum
import os
from pathlib import Path

from raymon.api import RaymonAPI

MB = 1000000


class RaymonLoggerBase(ABC):
    def __init__(self, project_id="default"):
        self.project_id = project_id
        self.setup_logger(stdout=True)

    def structure(self, ray_id, ref, data):
        return {
            "timestamp": str(pendulum.now("utc")),
            "ray_id": str(ray_id),
            "ref": ref,
            "data": data,
            "project_id": self.project_id,
        }

    def setup_logger(self, fname=None, stdout=True):
        # Set up the raymon logger
        logger = logging.getLogger("Raymon")
        if len(logger.handlers) == 0:
            logger.setLevel(logging.DEBUG)
            # Set level to debug -- will use debug messages for binary data
            formatter = logging.Formatter("{asctime} - {name} - {ray_id} - {message}", style="{")
            if stdout:
                # Add a stderr handler -- Do not send DEBUG messages to there (will contain binary data)
                sh = logging.StreamHandler(stream=sys.stdout)
                sh.setLevel(logging.INFO)
                sh.setFormatter(formatter)
                logger.addHandler(sh)
        self.logger = logger

    @abstractmethod
    def info(self, ray_id, text):
        pass

    @abstractmethod
    def log(self, ray_id, ref, data):
        pass

    @abstractmethod
    def tag(self, ray_id, tags):
        pass


class RaymonFileLogger(RaymonLoggerBase):
    KB = 1000
    MB = KB * 1000

    def __init__(self, path="/tmp/raymon/", project_id="default", reset_file=False):
        super().__init__(project_id=project_id)
        self.setup_datalogger(path=path, reset_file=reset_file)

    def setup_datalogger(self, path, reset_file=False):
        # Set up the raymon logger
        logger = logging.getLogger("Raymon-data")
        self.data_logger = logger
        if len(logger.handlers) == 1 and isinstance(logger.handlers[0], RotatingFileHandler):
            if reset_file:
                print(f"Handler found, but reseting file.")
                logger.handlers = []
            else:
                # Already configured
                print(f"Skipping add handler", logger.handlers, flush=True)
                # traceback.print_stack()
                self.fname = logger.handlers[0].baseFilename
                return

        print(f"Adding handler")
        self.fname = Path(path) / f"raymon-{str(uuid.uuid4())}.log"
        logger.setLevel(logging.INFO)
        # Add a file handler
        fh = RotatingFileHandler(self.fname, maxBytes=200 * MB, backupCount=10)
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)

    def info(self, ray_id, text):
        jcr = self.structure(ray_id=ray_id, ref=None, data=text)
        kafka_msg = {"type": "info", "jcr": jcr}
        self.logger.info(text, extra=jcr)
        self.data_logger.info(json.dumps(kafka_msg))
        self.logger.info(f"Logged: {text}", extra=jcr)

    def log(self, ray_id, ref, data):
        jcr = self.structure(ray_id=ray_id, ref=ref, data=data.to_jcr())
        kafka_msg = {"type": "data", "jcr": jcr}
        self.logger.info(f"Logging data at {ref}", extra=jcr)
        self.data_logger.info(json.dumps(kafka_msg))
        self.logger.info(f"Logged ref {ref} data to textfile.", extra=jcr)

    def tag(self, ray_id, tags):
        jcr = self.structure(ray_id=ray_id, ref=None, data=tags)
        kafka_msg = {"type": "tags", "jcr": jcr}
        self.data_logger.info(json.dumps(kafka_msg))
        self.logger.info(f"Logged tags to textfile.", extra=jcr)


class RaymonAPILogger(RaymonLoggerBase):
    def __init__(self, url="http://localhost:8000", project_id=None, auth_path=None):
        super().__init__(project_id=project_id)
        self.api = RaymonAPI(url=url, project_id=project_id, auth_path=auth_path)

    """
    Functions related to logging of rays
    """

    def info(self, ray_id, text):
        # print(f"Logging Raymon Datatype...{type(data)}", flush=True)
        jcr = self.structure(ray_id=ray_id, ref=None, data=text)
        self.logger.info(text, extra=jcr)
        resp = self.api.post(
            route=f"projects/{self.project_id}/ingest",
            json=jcr,
        )
        status = "OK" if resp.ok else f"ERROR: {resp.status_code}"
        self.logger.info(f"Logged info. Status: {status}", extra=jcr)

    def log(self, ray_id, ref, data):
        # print(f"Logging Raymon Datatype...{type(data)}", flush=True)
        jcr = self.structure(ray_id=ray_id, ref=ref, data=data.to_jcr())
        self.logger.info(f"Logging data at {ref}", extra=jcr)
        resp = self.api.post(
            route=f"projects/{self.project_id}/ingest",
            json=jcr,
        )
        status = "OK" if resp.ok else f"ERROR: {resp.status_code}"
        self.logger.info(f"Data logged at {ref}. Status: {status}", extra=jcr)

    def tag(self, ray_id, tags):
        # TODO validate tags
        jcr = self.structure(ray_id=ray_id, ref=None, data=tags)
        resp = self.api.post(
            route=f"projects/{self.project_id}/rays/{ray_id}/tags",
            json=tags,
        )
        status = "OK" if resp.ok else f"ERROR: {resp.status_code}"
        self.logger.info(f"Ray tagged. Status: {status}", extra=jcr)
