import logging
import pendulum

class ContextFilter(logging.Filter):
    def __init__(self, context):
        self.context = context

    def filter(self, record):
        record.context = self.context
        return True


class Logger:
    def __init__(self, context, project_id):
        self.context = context
        self.project_id = project_id
        self.logger = setup_logger(context=context, stdout=True)

    def format(self, ray_id, peephole, data):
        return {
            'timestamp': str(pendulum.now()),
            'ray_id': str(ray_id),
            'peephole': peephole, 
            'data': data,
            'context': self.context,
            'project_id': self.project_id,
        }


def setup_logger(context, fname=None, stdout=True):
    # Set up the raymon logger
    logger = logging.getLogger("Raymon")
    if len(logger.handlers) > 0:
        # Already configured
        return logger
    logger.setLevel(logging.DEBUG)
    # Set level to debug -- will use debug messages for binary data
    logger.addFilter(ContextFilter(context))
    formatter = logging.Formatter("{asctime} - {name} - {context} - {message}", style='{')

    if fname is not None:
        # Add a file handler
        fh = logging.FileHandler(fname)
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)

    if stdout:
        # print(f"Adding stout")
        # Add a stderr handler -- Do not send DEBUG messages to there (will contain binary data)
        sh = logging.StreamHandler(stream=sys.stdout)
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)
        logger.addHandler(sh)
    return logger
