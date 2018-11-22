import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s "
                              "%(levelname)-6s "
                              "%(module)s(%(lineno)d)"
                              "%(name)s "  # name from log = logging.getLogger('server_v2')
                              "'%(message)s'")

handler = logging.FileHandler('log/client.log')

handler.setFormatter(formatter)

log.addHandler(handler)
