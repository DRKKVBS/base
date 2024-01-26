import json
import os
import shutil


from custom_logger import logger
from user import User
from utils import fs_helper, pkg_helper, helper



root = fs_helper.get_root_dir()

# Load the config file
try:
    with open(f"{root}/configs/config.json", "r") as f:
        data = json.load(f)
except Exception as e:
    logger.error(f"Error loading config file: {e}")
    exit(1)


# helper.run_command(["apt", "update"])
# helper.run_command(["snap", "remove", "--purge", "firefox"])

# Install packages from the packages directory
for pkg in os.listdir(os.path.normpath(f"{root}/packages/")):
    print(pkg)
    pkg_helper.install_package(pkg)

# helper.run_command(["apt", "update"])


# for pkg in data["packages"]["install"]:
#     pkg_helper.install_package(pkg)