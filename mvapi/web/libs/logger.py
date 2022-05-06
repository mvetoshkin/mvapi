from mvapi.libs.logger import logger as logger_
from mvapi.settings import settings


logger = logger_.getChild(settings.API_LOGGER_NAME)
