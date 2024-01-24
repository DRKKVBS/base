import json
import logging.config
import logging.handlers
import os


def main():
    currrent_dir = os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0]
    # Setup logging
    logger = logging.getLogger("config_logger")

    with open(os.path.normpath(f"{currrent_dir}/logging_config.json"), "r") as f:
        logging.config.dictConfig(config=json.load(f))

    logger.info("Hello Info!")
    logger.debug("Hello Debug!")
    logger.warning("Hello Warning!")
    logger.error("Hello Error!")
    logger.critical("Hello Critical!")


if __name__ == "__main__":
    main()
