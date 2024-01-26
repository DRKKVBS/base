import os
import shutil

from custom_logger import logger
from utils.helper import run_command
from user import User

def get_root_dir():
    """Get the root directory of the project."""
    return os.path.realpath(os.path.dirname(__file__)).split('scripts')[0]

def set_file_permissions(file_path: str, uid: int, gid: int, mode: int = 0o644):
    """Set the file permissions of a file."""
    file_path = os.path.normpath(file_path)
    try:
        logger.info(f"Set Ownership of {file_path}!")
        shutil.chown(file_path, uid, gid)  # type: ignore

        logger.info(f"Set Permissions of {file_path}!")
        os.chmod(file_path, mode)
    except FileNotFoundError as e:
        logger.error(f"File {file_path} not found!")


def make_immutable(path: str):
    '''Make a file or a directory immutable using Chattr.'''

    path = os.path.normpath(path)
    run_command(["chattr", "+i", path])


def make_mutable(path: str):
    '''Make a file or a directory mutable using Chattr.'''

    path = os.path.normpath(path)
    run_command(["chattr", "-i", path])


def add_desktop_app(user: User, visible_apps: list):

    applications_path = os.path.normpath(
        f"{user.get_home_dir()}/.local/share/applications/")

    for app in os.listdir("/usr/share/applications/"):

        if app.endswith(".desktop") and app not in os.listdir(applications_path):
            shutil.copyfile(os.path.normpath(
                f"/usr/share/applications/{app}"), os.path.normpath(f"{applications_path}/{app}"))

        shutil.chown(os.path.normpath(
            f"{applications_path}/{app}"), user.get_uid(), user.get_gid())

    for app in os.listdir(applications_path):

        if app in visible_apps:
            with open(os.path.normpath(f"{applications_path}/{app}"), "r+") as f:
                text = f.read()
                if "NoDisplay=True" in text:
                    text.replace("NoDisplay=True", "NoDisplay=False")
                elif "NoDisplay=False" in text:
                    break
                elif "NoDisplay" not in text:
                    text.replace("[Desktop Entry]",
                                 "[Desktop Entry]\nNoDisplay=False")
        else:
            with open(os.path.normpath(f"{applications_path}/{app}"), "r+") as f:
                text = f.read()
                if "NoDisplay=True" in text:
                    break
                elif "NoDisplay=False" in text:
                    text.replace("NoDisplay=False", "NoDisplay=True")

                elif "NoDisplay" not in text:
                    text.replace("[Desktop Entry]",
                                 "[Desktop Entry]\nNoDisplay=True")

