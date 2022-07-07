import os

from configparser import ConfigParser

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = f'{PROJECT_ROOT}/src/config.ini'
SECTION = 'pyrogram'


def get():
    config = ConfigParser()
    config.read(CONFIG_PATH)
    return tuple(item[1] for item in config.items(SECTION))
