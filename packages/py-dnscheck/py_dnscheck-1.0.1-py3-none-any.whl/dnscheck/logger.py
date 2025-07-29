import logging

logger = logging.getLogger("dnscheck")

def setup_logger(verbose=False):
    if verbose:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
    else:
        logger.addHandler(logging.NullHandler())
