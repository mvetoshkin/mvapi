import logging


def init_logger(verbosity):
    logging.basicConfig(
        level=logging.DEBUG if verbosity else logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s: %(message)s',
    )
