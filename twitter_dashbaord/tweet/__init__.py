import logging

from twitter_dashbaord import settings

logging.basicConfig(filename=settings.LOG_FILENAME, level=logging.DEBUG)
