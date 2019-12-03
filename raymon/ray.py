import uuid


def _parse_rayid(ray_id):
    # rayid is a tuple, with an element per level
    if isinstance(ray_id, str):
        return = (ray_id)
    elif isinstance(ray_id, tuple):
        return ray_id
    elif ray_id is None:
        return (uuid.uuid4())


class Ray:
    
    def __init__(self, logger, ray_id=None, parent=None):
        self.ray_id = _parse_ray_id(ray_id)
        self.logger = logger
        self.context = logger.context

    """
    Methods related to data logging
    """
    def log_text(self, peephole, data):
        self.logger.log_text(ray_id=self.ray_id, peephole=peephole, data=data)

    def log_numpy(self, ray_id, peephole, data):
        self.logger.log_numpy(ray_id=self.ray_id, peephole=peephole, data=data)
    
    """
    Methods related to splitting and merging
    """
    def split(self, suffix=None):
        if suffix is None:
            suffix = uuid.uuid4()
        new_id = self.ray_id + (suffix)
        return Ray(self.logger, ray_id=ray_id, parent=self)
        
    
    def __str__(self):
        return "::".join(self.ray_id)
    



    
