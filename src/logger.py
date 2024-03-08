import json
import logging
import pathlib
import logging.config
import logging.handlers


def setup_logging():
    config_file = pathlib.Path("loggs/config.json")
    with open(config_file) as f:
        config = json.load(f)
    logging.config.dictConfig(config)
