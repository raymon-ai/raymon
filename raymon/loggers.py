import json
import uuid
import logging
from logging.handlers import DatagramHandler, RotatingFileHandler
import sys
from abc import ABC, abstractmethod
import pendulum
import os
from pathlib import Path

from raymon.tags import Tag
from raymon.globals import DataException, Serializable
from raymon import RaymonAPI

KB = 1000
MB = KB * 1000


class RaymonLoggerBase(ABC):
    def __init__(self, project_id="default"):
        self.project_id = project_id
        self.setup_logger(stdout=True)

    def to_json_serializable(self, data):
        """
        Makes sure all data is JSON serializable
        """

        if isinstance(data, str):  ## Infor messages are strings
            data = data
        elif isinstance(data, Serializable):
            data = data.to_jcr()
        elif isinstance(data, list):
            dc = []
            for d in data:
                if isinstance(d, Serializable):
                    dc.append(d.to_jcr())
                else:
                    dc.append(d)  # We assume d is JSON serializable
            data = dc
        # Else: assume dat is JSON serializble
        return data

    def structure(self, trace_id, ref, data):
        data = self.to_json_serializable(data)
        return {
            "timestamp": str(pendulum.now("utc")),
            "trace_id": str(trace_id),
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
            formatter = logging.Formatter("{asctime} - {name} - {trace_id} - {message}", style="{")
            if stdout:
                # Add a stderr handler -- Do not send DEBUG messages to there (will contain binary data)
                sh = logging.StreamHandler(stream=sys.stdout)
                sh.setLevel(logging.INFO)
                sh.setFormatter(formatter)
                logger.addHandler(sh)
        self.logger = logger

    @abstractmethod
    def info(self, trace_id, text):
        pass

    @abstractmethod
    def log(self, trace_id, ref, data):
        pass

    @abstractmethod
    def tag(self, trace_id, tags):
        pass

    def parse_tags(self, tags):
        parsed_tags = []
        for tag in tags:
            if isinstance(tag, Tag):
                parsed_tags.append(tag)
            elif isinstance(tag, dict):
                parsed = Tag.from_jcr(tag)
                parsed_tags.append(parsed)
            else:
                raise DataException(f"{type(tag)} not supported as Tag")
        return parsed_tags


class RaymonFileLogger(RaymonLoggerBase):
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

    def info(self, trace_id, text):
        jcr = self.structure(trace_id=trace_id, ref=None, data=text)
        kafka_msg = {"type": "info", "jcr": jcr}
        self.data_logger.info(json.dumps(kafka_msg))
        self.logger.info(f"Logged: {text}", extra=jcr)

    def log(self, trace_id, ref, data):
        jcr = self.structure(trace_id=trace_id, ref=ref, data=data.to_jcr())
        kafka_msg = {"type": "data", "jcr": jcr}
        self.data_logger.info(json.dumps(kafka_msg))
        self.logger.info(f"Logged ref {ref} data to textfile.", extra=jcr)

    def tag(self, trace_id, tags):
        tags = self.parse_tags(tags)
        jcr = self.structure(trace_id=trace_id, ref=None, data=tags)
        kafka_msg = {"type": "tags", "jcr": jcr}
        self.data_logger.info(json.dumps(kafka_msg))
        self.logger.info(f"Logged tags to textfile.", extra=jcr)


class RaymonAPILogger(RaymonLoggerBase):
    def __init__(self, url="http://localhost:8000", project_id=None, auth_path=None, env=None):
        super().__init__(project_id=project_id)
        self.api = RaymonAPI(url=url, project_id=project_id, auth_path=auth_path, env=env)

    """
    Functions related to logging of traces
    """

    def info(self, trace_id, text):
        # print(f"Logging Raymon Datatype...{type(data)}", flush=True)
        jcr = self.structure(trace_id=trace_id, ref=None, data=text)
        self.logger.info(text, extra=jcr)
        resp = self.api.post(
            route=f"projects/{self.project_id}/ingest",
            json=jcr,
        )
        status = "OK" if resp.ok else f"ERROR: {resp.status_code}"
        self.logger.info(f"Logged info. Status: {status}", extra=jcr)

    def log(self, trace_id, ref, data):
        # print(f"Logging Raymon Datatype...{type(data)}", flush=True)
        jcr = self.structure(trace_id=trace_id, ref=ref, data=data.to_jcr())
        self.logger.info(f"Logging data at {ref}", extra=jcr)
        resp = self.api.post(
            route=f"projects/{self.project_id}/ingest",
            json=jcr,
        )
        status = "OK" if resp.ok else f"ERROR: {resp.status_code}"
        self.logger.info(f"Data logged at {ref}. Status: {status}", extra=jcr)

    def tag(self, trace_id, tags):
        tags = self.parse_tags(tags)
        jcr = self.structure(trace_id=trace_id, ref=None, data=tags)
        resp = self.api.post(
            route=f"projects/{self.project_id}/traces/{trace_id}/tags",
            json=jcr,
        )
        status = "OK" if resp.ok else f"ERROR: {resp.status_code}"
        self.logger.info(f"Ray tagged. Status: {status}", extra=jcr)
