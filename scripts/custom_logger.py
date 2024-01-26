import json
import logging.config
import logging.handlers
import os

# Get root directory of the script
root = os.path.realpath(
    os.path.dirname(__file__)).split('scripts')[0]

# Setup logging
logger = logging.getLogger("config_logger")

# Load logging configuration
with open(os.path.normpath(f"{root}/configs/logging_config.json"), "r") as f:
    logging.config.dictConfig(config=json.load(f))
