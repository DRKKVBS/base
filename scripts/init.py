import json
import utils
from utils import filesystem, utils, user_helper, package
import os
import main
from custom_logger import logger


root_dir = filesystem.get_root_dir()

# Install packages from the packages directory
with open(os.path.normpath(f"{root_dir}/configs/config.json"), "r") as f:
    data = json.load(f)

# Promt the user to enter a hostname if none is set
if data["hostname"] == None:
    data["hostname"] = input(
        "Please enter a hostname for the system and press enter to continue...\n")
    logger.info(f"Hostname set to {data['hostname']}")


if data["users"]["admin"]["password"] == None:
    data["users"]["admin"]["password"] = utils.input_validation(
        "Please enter a password for the Administrator account and press enter to continue...")
    logger.info(
        f"Administrator password set to {data['users']['admin']['password']}")


with open(os.path.normpath(f"{root_dir}/configs/config.json"), "w") as f:
    json.dump(data, f)


utils.run_command(["apt", "update"])
utils.run_command(["snap", "remove", "--purge", "firefox"])
utils.run_command(["apt", "upgrade", "-y"])

# Install packages from the packages directory
for pkg in os.listdir(os.path.normpath(f"{root_dir}/packages/")):
    package.install_package(pkg)

utils.run_command(["apt", "update"])


for pkg in data["packages"]["install"]:
    package.install_package(pkg)

for pkg in data["packages"]["remove"]:
    utils.run_command(["apt", "remove", "-y", pkg])

for cmd in [["apt", "update"], ["apt", "upgrade", "-y"],
            ["apt", "purge", "-y", "gnome-initial-setup"],
            ["pip3", "install", "--upgrade", "pip"],
            ["pip3", "install", "-r", "../data/pip-requirements.txt"]]:
    utils.run_command(cmd)


main.main()

for cmd in [["dconf", "update"], ["grub-mkconfig", "-o", "/boot/grub/grub.cfg"], ["reboot"]]:
    utils.run_command(cmd)
