import json
import utils
import os
import main
from getpass import getpass


root_dir = utils.get_root_dir()

# Install packages from the packages directory
with open(os.path.normpath(f"{root_dir}/script_configs/config.json")) as f:
    data = json.load(f)

# Promt the user to enter a hostname if none is set
if data["hostname"] == None:
    data["hostname"] = input(
        "Please enter a hostname for the system and press enter to continue...\n")

if data["users"]["admin"]["password"] == None:
    data["users"]["admin"]["password"] = getpass(
        "Please enter a hostname for the system and press enter to continue...\n")

# utils.run_command(["apt", "update"])
# utils.run_command(["snap", "remove", "--purge", "firefox"])
# utils.run_command(["apt", "upgrade", "-y"])

# # Install packages from the packages directory
# for pkg in os.listdir(os.path.normpath(f"{root_dir}/packages/")):
#     utils.install_package(pkg)

# utils.run_command(["apt", "update"])


# for pkg in data["apt_packages"]:
#     utils.install_package(pkg)


# utils.run_command(["apt", "update"])
# utils.run_command(["apt", "upgrade", "-y"])

# utils.run_command(["apt", "purge", "-y", "gnome-initial-setup"])
# utils.run_command(["pip3", "install", "--upgrade", "pip"])
# utils.run_command(["pip3", "install", "-r", "../data/pip-requirements.txt"])

# main.main()
# utils.run_command(["dconf", "update"])
# utils.run_command(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"])
# utils.run_command(["reboot"])
