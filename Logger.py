import coloredlogs, logging

class Logger():

    Log = None

    @classmethod
    def Initialize(cls):
        cls.Log = logging.getLogger(__name__)
        coloredlogs.install(
            fmt='[%(asctime)s] [%(levelname)s]: %(message)s',
            level='INFO',
            logger=cls.Log)