import json
import uuid
import logging
import sys
import pendulum
import os
from pathlib import Path

from raymon.tags import Tag
from raymon.globals import DataException, Serializable
from raymon import RaymonAPI

KB = 1000
MB = KB * 1000


class RaymonAPILogger:
    def __init__(self, project_id, url="https://api.raymon.ai/v0", auth_path=None, env=None, batch_size=1):
        self.project_id = project_id
        self.setup_stdout(stdout=True)
        self.api = RaymonAPI(url=url, project_id=project_id, auth_path=auth_path, env=env)
        self.buffer = []
        self.batch_size = batch_size

    """
    Functions related to logging of traces
    """

    def info(self, trace_id, text):
        # print(f"Logging Raymon Datatype...{type(data)}", flush=True)
        jcr = self.structure(dtype="info", trace_id=trace_id, data=text)
        self.stdout.info(text, extra=jcr)
        self.buffer.append(jcr)
        self.stdout.info("Added info to buffer.", extra=jcr)
        self.check_flush()

    def log(self, trace_id, ref, data):
        # print(f"Logging Raymon Datatype...{type(data)}", flush=True)
        jcr = self.structure(dtype="object", trace_id=trace_id, ref=ref, data=data.to_jcr())
        self.buffer.append(jcr)
        self.stdout.info(f"Added data to buffer for {ref}", extra=jcr)
        self.check_flush()

    def tag(self, trace_id, tags):
        tags = self.parse_tags(tags)
        jcr = self.structure(dtype="tags", trace_id=trace_id, ref=None, data=tags)
        self.buffer.append(jcr)
        self.stdout.info("Added tags to buffer", extra=jcr)
        self.check_flush()

    def flush(self):
        resp = self.api.post(
            route=f"projects/{self.project_id}/ingest_batch",
            json=self.buffer,
        )
        status = "OK" if resp.ok else f"ERROR: {resp.status_code}"
        self.stdout.info(f"Posted buffer. Status: {status}", extra={"trace_id": None})

        if resp.ok:
            self.buffer = []
        else:
            print(resp.text)

    def check_flush(self):
        if len(self.buffer) >= self.batch_size:
            self.flush()

    """Helpers"""

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
        # Else: assume data is JSON serializble
        return data

    def structure(self, dtype, trace_id, data, ref=None):
        data = self.to_json_serializable(data)
        return {
            "dtype": dtype,
            "timestamp": str(pendulum.now("utc")),
            "trace_id": str(trace_id),
            "project_id": self.project_id,
            "ref": ref,
            "data": data,
        }

    def setup_stdout(self, stdout=True):
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
        self.stdout = logger

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
