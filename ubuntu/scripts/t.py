import json
import logging.config
import logging.handlers
import os
import custom_logger


def main():
    logger = custom_logger.setup_logging()

    logger.info("Hello Info!")
    logger.debug("Hello Debug!")
    logger.warning("Hello Warning!")
    logger.error("Hello Error!")
    logger.critical("Hello Critical!")


if __name__ == "__main__":
    main()
