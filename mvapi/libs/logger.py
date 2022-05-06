import logging
import logging.config

from mvapi.settings import settings

logger = logging.getLogger(settings.ROOT_LOGGER_NAME)


def init_logger():
    if settings.LOGGING:
        logging.config.dictConfig(settings.LOGGING)
