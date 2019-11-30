import logging

class ContextFilter(logging.Filter):
    def __init__(self, context):
        self.context = context

    def filter(self, record):
        record.context = self.context
        return True


def setup_logger(fname, context, stdout=True):
    # Set up the raymon logger
    logger = logging.getLogger("Raymon")
    logger.setLevel(logging.DEBUG)
    # Set level to debug -- will use debug messages for binary data
    logger.addFilter(ContextFilter(context))
    formatter = logging.Formatter("{asctime} - {name} - {context} - {message}", style='{')

    # Add a file handler
    fh = logging.FileHandler(fname)
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    if stdout:
        print(f"Adding stout")
        # Add a stderr handler -- Do not send DEBUG messages to there (will contain binary data)
        sh = logging.StreamHandler(stream=sys.stdout)
        sh.setLevel(logging.INFO)
        sh.setFormatter(formatter)
        logger.addHandler(sh)
    return logger
