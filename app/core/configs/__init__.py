"""
Config Module
"""

from functools import lru_cache

from app.core.configs.environment import Environment
from app.core.configs.logger import Logger


@lru_cache()
def get_environment():
    """Helper function to get env with lru cache"""
    return Environment()


@lru_cache()
def get_logger(name):
    """Helper function to get Logger"""
    return Logger(name=name).get_logger()
