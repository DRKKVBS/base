import json
import utils
import os
import main
import custom_logger


root_dir = utils.get_root_dir()

logger = custom_logger.setup_logging()

# Install packages from the packages directory
with open(os.path.normpath(f"{root_dir}/script_configs/config.json"), "r") as f:
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


with open(os.path.normpath(f"{root_dir}/script_configs/config.json"), "w") as f:
    json.dump(f, data)


utils.run_command(["apt", "update"])
utils.run_command(["snap", "remove", "--purge", "firefox"])
utils.run_command(["apt", "upgrade", "-y"])

# Install packages from the packages directory
for pkg in os.listdir(os.path.normpath(f"{root_dir}/packages/")):
    utils.install_package(pkg)

utils.run_command(["apt", "update"])


for pkg in data["apt_packages"]:
    utils.install_package(pkg)

for cmd in [["apt", "update"], ["apt", "upgrade", "-y"],
            ["apt", "purge", "-y", "gnome-initial-setup"],
            ["pip3", "install", "--upgrade", "pip"],
            ["pip3", "install", "-r", "../data/pip-requirements.txt"]]:
    utils.run_command(cmd)


main.main()

for cmd in [["dconf", "update"], ["grub-mkconfig", "-o", "/boot/grub/grub.cfg"], ["reboot"]]:
    utils.run_command(cmd)
