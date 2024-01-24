import json
import logging.config
import logging.handlers
import os


def main():
    # Setup logging
    logger = logging.getLogger("config_logger")

    with open(os.path.normpath(f"{os.path.dirname(__file__)}/logging_config.json"), "r") as f:
        logging.config.dictConfig(config=json.load(f))

    logger.info("Hello Info!")
    logger.debug("Hello Debug!")
    logger.warning("Hello Warning!")
    logger.error("Hello Error!")
    logger.critical("Hello Critical!")


if __name__ == "__main__":
    main()
