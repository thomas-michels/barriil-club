"""
Looger Module
"""
import logging
import os


class RelativePathFormatter(logging.Formatter):
    def format(self, record):
        # Calcula o caminho relativo
        record.relativepath = os.path.relpath(record.pathname, os.getcwd())
        return super().format(record)


class Logger:
    """
    Logger class
    """

    INFO = logging.INFO
    DEBUG = logging.DEBUG
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITITAL = logging.CRITICAL

    def __init__(self, name=__name__):
        # create logger
        self.logger_worker = logging.getLogger(name)
        self.__config_logger()

    def __config_logger(self):
        """
        Config logger
        """
        self.logger_worker.setLevel(self.DEBUG)
        self.__config_handler(logging.DEBUG)
        self.__config_handler(logging.DEBUG, "debug.log")

    def __config_handler(self, level, file=None):
        # create console handler and set level to debug
        console_handler = logging.FileHandler(file) if file else logging.StreamHandler()
        console_handler.setLevel(level)

        # create formatter
        formatter = RelativePathFormatter(
            "%(levelname)s\t| %(asctime)s| %(relativepath)s:%(lineno)s => %(message)s\t"
        )

        # add formatter to console_handler
        console_handler.setFormatter(formatter)

        # add console_handler to logger
        self.logger_worker.addHandler(console_handler)

    def get_logger(self):
        """
        Log message
        """
        return self.logger_worker
