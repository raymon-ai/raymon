import json
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

    def structure(self, ray_id, peephole, data):
        return {
            "timestamp": str(pendulum.now("utc")),
            "ray_id": str(ray_id),
            "peephole": peephole,
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
    def log(self, ray_id, peephole, data):
        pass

    @abstractmethod
    def tag(self, ray_id, tags):
        pass


class RaymonFileLogger(RaymonLoggerBase):
    KB = 1000
    MB = KB * 1000

    def __init__(self, path="/tmp/raymon/", project_id="default"):
        super().__init__(project_id=project_id)
        self.fname = Path(path) / f"raymon-{os.getpid()}.log"
        self.setup_datalogger()

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

        self.data_logger = logger

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


class RaymonAPILogger(RaymonLoggerBase):
    def __init__(self, url="http://localhost:8000", project_id=None, auth_path=None):
        super().__init__(project_id=project_id)
        self.api = RaymonAPI(url=url, project_id=project_id, auth_path=auth_path)

    """
    Functions related to logging of rays
    """

    def info(self, ray_id, text):
        # print(f"Logging Raymon Datatype...{type(data)}", flush=True)
        jcr = self.structure(ray_id=ray_id, peephole=None, data=text)
        self.logger.info(text, extra=jcr)
        resp = self.api.post(
            route=f"projects/{self.project_id}/ingest",
            json=jcr,
        )
        status = "OK" if resp.ok else f"ERROR: {resp.status_code}"
        self.logger.info(f"Logged info. Status: {status}", extra=jcr)

    def log(self, ray_id, peephole, data):
        # print(f"Logging Raymon Datatype...{type(data)}", flush=True)
        jcr = self.structure(ray_id=ray_id, peephole=peephole, data=data.to_jcr())
        self.logger.info(f"Logging data at {peephole}", extra=jcr)
        resp = self.api.post(
            route=f"projects/{self.project_id}/ingest",
            json=jcr,
        )
        status = "OK" if resp.ok else f"ERROR: {resp.status_code}"
        self.logger.info(f"Data logged at {peephole}. Status: {status}", extra=jcr)

    def tag(self, ray_id, tags):
        # TODO validate tags
        jcr = self.structure(ray_id=ray_id, peephole=None, data=tags)
        resp = self.api.post(
            route=f"projects/{self.project_id}/rays/{ray_id}/tags",
            json=tags,
        )
        status = "OK" if resp.ok else f"ERROR: {resp.status_code}"
        self.logger.info(f"Ray tagged. Status: {status}", extra=jcr)
