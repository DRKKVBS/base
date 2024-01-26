import json
import os
import shutil

from importlib import resources

import utils
from custom_logger import logger
from user import User


def main():

    root = utils.get_root_dir()

    # Load the config file
    try:
        with open(f"{root}/script_configs/config.json", "r") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading config file: {e}")
        exit(1)

    # Create missing directories
    # Needed to copy files later on
    for missing_dir in ["/etc/firefox/policies/", "/usr/share/drk/"]:
        try:
            logger.info(f"Creating directory {missing_dir}")
            os.makedirs(f"{missing_dir}", exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating directory {missing_dir}: {e}")

    # Create users
    users = []
    for _, user_data in data["users"].items():
        users.append(
            User(username=user_data["username"], password=user_data["password"], sudo=user_data["sudo"], desktop_entries=user_data["desktop"]))

    # Copy files
    for _, paths in data["files_to_copy"].items():
        try:
            shutil.copyfile(os.path.normpath(
                f"{root}/data/{paths['source']}"), f"{paths['destination']}")
        except Exception as e:
            logger.error(f"Error copying file: {e}")

    # Copy directories
    for _, paths in data["dirs_to_copy"].items():
        try:
            shutil.copytree(os.path.normpath(
                f"{root}/data/{paths['source']}"), f"{paths['destination']}", dirs_exist_ok=True)
        except Exception as e:
            logger.error(f"Error copying directory: {e}")

    # Setup user specific configurations
    for user in users:

        # Copy custom desktop entries
        shutil.copytree(os.path.normpath(f"{root}/data//DesktopEntries/"),
                        os.path.normpath(f"{user.get_home_dir()}/.local/share/applications/"), dirs_exist_ok=True)

        # Set environment variables
        with open(os.path.normpath(f"{user.get_home_dir()}/.profile"), "a+") as f:
            f.write("# Set environment variables\n")
            f.write(
                f"export DCONF_PROFILE={user.username}\n")

        with open(os.path.normpath(f"{user.get_home_dir()}/.config/mimeapps.list"), "a+") as f:
            if f.read() != "":
                f.write(
                    "[Default Applications]\napplication/ica=icaclient.desktop")
            else:
                f.write("application/ica=icaclient.desktop")

        for path in ["/var/lib/snapd/desktop/applications/", "/usr/share/applications/"]:
            for app in os.listdir(path):
                if app.endswith(".desktop"):
                    shutil.copyfile(os.path.normpath(
                        f"{path}/{app}"), os.path.normpath(f"{user.get_home_dir()}/.local/share/applications/{app}"))
                    with open(os.path.normpath(f"{user.get_home_dir()}/.local/share/applications/{app}"), "r+") as f:
                        content = f.read()
                        if app in user.desktop_entries:
                            if "NoDisplay=true" in content:
                                content = content.replace(
                                    "NoDisplay=true", "NoDisplay=false")
                            elif "NoDisplay=false" not in content:
                                content = content.replace(
                                    "[Desktop Entry]", "[Desktop Entry]\nNoDisplay=false")
                        else:
                            if "NoDisplay=false" in content:
                                content = content.replace(
                                    "NoDisplay=false", "NoDisplay=true")
                            elif "NoDisplay=true" not in content:
                                content = content.replace(
                                    "[Desktop Entry]", "[Desktop Entry]\nNoDisplay=true")
                        f.seek(0)
                        f.truncate()
                        f.write(content)

        # Set file permissions for desktop entries
        for file in os.listdir(os.path.normpath(f"/{user.get_home_dir()}/.local/share/applications/")):
            try:
                shutil.chown(file, user=user.get_uid(), group=user.get_gid())
                os.chmod(file, 0o664)
            except Exception as e:
                logger.error(f"Error setting file permissions: {e}")

            utils.set_file_permissions(
                f"/{user.get_home_dir()}/.local/share/applications/{file}", user.get_uid(), user.get_gid(), 0o664)


if __name__ == "__main__":

    # # Initialize parser
    # parser = argparse.ArgumentParser(
    #     prog="DRK Ubuntu Configurator",
    #     description="Configures the the Ubuntu Linux, after the OS Installation.",
    #     epilog="Placeholder.",)

    # # Adding optional argument
    # parser.add_argument("-t", "--Type", action="store", required=True, type=str,
    #                     choices=["thin", "mobile"], help="Type of Device.",)

    # parser.add_argument("-c", "--Configuration", action="store", required=True, type=str,
    #                     choices=["base", "usb"], help="Type of Configuration to be used.",)

    # parser.add_argument("-hn", "--Hostname", action="store",
    #                     type=str, help="The hostname of the new system.")

    # # Read arguments from command line
    # args = parser.parse_args()

    # if args.Hostname != None:
    #     hostname = args.Hostname
    # else:
    #     hostname = f"drk-bs-{args.Type}-{args.Configuration}"

    main()
    # utils.test()
