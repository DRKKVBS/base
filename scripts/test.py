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

# Promt the user to enter a hostname if none is set
if data["hostname"] == None:
    data["hostname"] = input(
        "Please enter a hostname for the system and press enter to continue...\n")
    logger.info(f"Hostname set to {data['hostname']}")

with open("/etc/hostname", "w") as f:
    f.write(data["hostname"] + "\n")


if data["users"]["admin"]["password"] == None:
    data["users"]["admin"]["password"] = helper.input_validation(
        "Please enter a password for the Administrator account and press enter to continue...")
    logger.info(
        f"Administrator password set to {data['users']['admin']['password']}")


helper.run_command(["apt", "update"])
helper.run_command(["snap", "remove", "--purge", "firefox"])

# Install packages from the packages directory
for pkg in os.listdir(os.path.normpath(f"{root}/packages/")):
    print(pkg)
    pkg_helper.install_package(pkg)

helper.run_command(["apt", "update"])


for pkg in data["packages"]["install"]:
    pkg_helper.install_package(pkg)