import logging
from logging.handlers import TimedRotatingFileHandler

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s "
                              "%(levelname)-8s "
                              "%(module)s(%(lineno)d) "
                              "%(name)s "  # name from log = logging.getLogger('server_v2')
                              "'%(message)s'")

handler = TimedRotatingFileHandler('log/server_v2.log',
                                   when="midnight",
                                   interval=1,
                                   backupCount=5)

handler.setFormatter(formatter)

log.addHandler(handler)
