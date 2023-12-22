import json
import os
import shutil
import utils

from user import User


def main():

    # Set the directory depending on the location of the script
    currrent_dir = os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0]
    data_dir = os.path.normpath(f"{currrent_dir}/data/")

    # Create missing dirs
    for missing_dir in ["/etc/firefox/policies/", "/usr/share/icons/DRK/", "/usr/share/firefox/"]:
        os.makedirs(f"{missing_dir}", exist_ok=True)

    # Load the config file
    with open(f"{data_dir}/config.json", "r") as f:
        data = json.load(f)

    # Install packages
    for download_url in data["wget_packages"]:
        package = download_url.split("/")[-1]
        utils.run_command(["wget", download_url, "-O", package])
        utils.install_package(package, file_path=f"./{package}")
    for package in data["apt_packages"]:
        utils.install_package(package)
    utils.install_package(
        "icaclient", f"{data_dir}/icaclient_23.11.0.82_amd64.deb")

    # Create users
    users = []
    for _, user_data in data["users"].items():
        users.append(
            User(username=user_data["username"], password=user_data["password"], sudo=user_data["sudo"], dekstop_entries=user_data["desktop"]))

    # Copy files
    for _, paths in data["files_to_copy"].items():
        shutil.copyfile(
            f"{data_dir}/{paths['source']}", f"{paths['destination']}")

    # Copy directories
    for _, paths in data["dirs_to_copy"].items():
        shutil.copytree(
            f"{data_dir}/{paths['source']}", f"{paths['destination']}", dirs_exist_ok=True)

    # Setup user specific configurations
    for user in users:
        # Copy custom desktop entries
        shutil.copytree(f"{data_dir}/DesktopEntries/",
                        os.path.normpath(f"{user.get_home_dir()}/.local/share/applications/"), dirs_exist_ok=True)

        # Set environment variables
        with open(os.path.normpath(f"{user.home_dir}/.profile"), "a") as f:
            f.write("# Set environment variables\n")
            f.write(
                f"export DCONF_PROFILE={user.username}\n")

        # Set file permissions for desktop entries
        for file in os.listdir(os.path.normpath(f"/{user.home_dir}/.local/share/applications/")):
            utils.set_file_permissions(
                f"/{user.home_dir}/.local/share/applications/{file}", user.uid, user.gid, 0o664)


if __name__ == "__main__":
    main()
