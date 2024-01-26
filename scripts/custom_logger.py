import logging.config
import logging.handlers
import json
import os


currrent_dir = os.path.realpath(
    os.path.dirname(__file__)).split('scripts')[0]
# Setup logging
logger = logging.getLogger("config_logger")

with open(os.path.normpath(f"{currrent_dir}/script_configs/logging_config.json"), "r") as f:
    logging.config.dictConfig(config=json.load(f))

