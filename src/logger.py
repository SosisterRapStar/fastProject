import json
import logging
import pathlib
import logging.config
import logging.handlers
from abc import ABC, abstractmethod


def setup_logging():
    config_file = pathlib.Path("loggs/config.json")
    with open(config_file) as f:
        config = json.load(f)
    logging.config.dictConfig(config)
    return config
