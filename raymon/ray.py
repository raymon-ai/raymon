import uuid
import numpy as np


def _parse_ray_id(ray_id):
    # rayid is a tuple, with an element per level
    if isinstance(ray_id, str):
        return (ray_id,)
    elif isinstance(ray_id, tuple):
        return ray_id
    elif ray_id is None:
        return (str(uuid.uuid4()),)


def _match_prefix(raylist):
    ids = [str(ray) for ray in raylist]
    shortest_idx = np.argmin(len(idstr) for idstr in ids)
    shortest = ids[shortest_idx]

    for i in range(len(shortest) - 1):
        if not all(idstr.startswith(shortest[: i + 1]) for idstr in ids):
            if i == 1:
                raise Exception(f"No common prefix found for rays: {raylist}")
            break
    match_len = i
    prefix = tuple(shortest[:match_len].split(":"))
    return prefix


class Ray:
    def __init__(self, logger, ray_id=None, pred=None):
        self.ray_id = _parse_ray_id(ray_id)
        self.logger = logger
        self.pred = pred

    """
    Methods related to data logging
    """

    def info(self, text):
        self.logger.info(ray_id=str(self), text=text)

    def log(self, peephole, data):
        self.logger.log(ray_id=str(self), peephole=peephole, data=data)

    def tag(self, tags):
        self.logger.tag(ray_id=str(self), tags=tags)

    """
    Methods related to splitting and merging
    """

    def split(self, suffix=None):
        if suffix is None:
            suffix = uuid.uuid4()
        new_id = self.ray_id + (suffix,)
        return Ray(self.logger, ray_id=new_id, pred=self)

    @classmethod
    def merge(cls, raylist, suffix):
        # Check whether it is a list
        if not isinstance(raylist, list):
            raise ValueError("Input type should be a list of Rays")
        # Find prefix that matches all rays
        prefix = _match_prefix(raylist)
        ref_logger = raylist[0].logger
        # Add suffix
        new_id = prefix + (suffix,)
        return Ray(ref_logger, ray_id=new_id, pred=raylist)

    def __str__(self):
        return ":".join(self.ray_id)
