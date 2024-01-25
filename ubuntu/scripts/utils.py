import json
import logging.config
import logging.handlers
import os
import pwd
import shutil
from subprocess import PIPE, STDOUT, Popen, run, CalledProcessError
import sys
from user import User
import custom_logger

# Setup logging
logger = custom_logger.setup_logging()


def merge_and_update_dicts(dict1: dict, dict2: dict):
    """ Merge two json files. Extending lists or dictonaries and update values."""
    for k, v in dict1.items():
        if k not in dict2.keys():
            dict2[k] = v
        if type(v) == list:
            dict2[k].extend(v)
            temp_lst = list(dict.fromkeys(dict2[k]))
            dict2[k].clear()
            dict2[k].extend(temp_lst)
            dict2[k].sort()
        elif type(v) == dict:
            dict2[k] = merge_and_update_dicts(dict1[k], dict2[k])
        else:
            dict1[k] = dict2[k]
    return dict2


def chmod_recursive(root_path: str, mode: int, uid: int, gid: int):
    """Change permissions recursively for directories."""

    # Change permissions for the top-level folder
    os.chmod(root_path, mode)
    logger.info(f"Changed permissions for {root_path} to {mode}")
    for root, dirs, files in os.walk(root_path):
        # Set perms on sub-directories
        for dir in dirs:

            dir = os.path.join(root, dir)
            os.chown(dir, uid=uid, gid=gid)  # type: ignore
            logger.info(f"Changed Ownership for {dir} to {uid}:{gid}")
            os.chmod(dir, mode)
            logger.info(f"Changed permissions for {dir} to {uid}:{gid}")

        # Set perms on files
        for file in files:
            file = os.path.join(root, file)
            os.chown(file, uid=uid, gid=gid)  # type: ignore
            logger.info(f"Changed Ownership for {file} to {uid}:{gid}")

            os.chmod(file, mode)
            logger.info(f"Changed permissions for {file} to {uid}:{gid}")


def set_hostname(hostname: str):
    """Set the hostname of the system."""

    try:
        with open("/etc/hostname", "w") as f:
            logger.info(f"Changing hostname to {hostname}")
            f.write(hostname)
    except Exception as e:
        logger.error(e)


def install_package(package_name: str, file_path=None):
    """Install a package using apt."""

    logger.info(f"Installing {package_name}")

    if package_is_installed(package_name):
        logger.info(f"Skipping {package_name}. It is already installed")
    else:

        # Install the package from the file if a file path is given
        package_name = package_name if file_path == None else file_path
        run_command(["apt", "install", "-y", package_name])


def package_is_installed(package_name: str):
    """Check if a package is installed."""

    return True if run_command(["dpkg", "-l", package_name]) != None else False


def get_uid(user: str):
    """Get the uid of a user."""

    try:
        return pwd.getpwnam(user).pw_uid  # type: ignore
    except KeyError:
        logger.error(f"User {user} not found!")
        raise


def get_gid(user: str):
    """Get the gid of a user."""

    try:
        return pwd.getpwnam(user).pw_gid  # type: ignore
    except KeyError:
        logger.error(f"User {user} not found!")
        raise


def get_home_dir(user: str):
    """Get the gid of a user."""

    try:
        return pwd.getpwnam(user).pw_gid  # type: ignore
    except KeyError:
        logger.error(f"User {user} not found!")
        raise


def set_file_permissions(file_path: str, uid: int, gid: int, mode: int = 0o644):
    """Set the file permissions of a file."""
    file_path = os.path.normpath(file_path)
    try:
        logger.info(f"Set Ownership of {file_path}!")
        os.chown(file_path, uid, gid)  # type: ignore

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


def run_command(cmds: list):
    """Run a command using  the subprocess library."""

    try:
        logger.info(f"Executing: {cmds}")

        process = Popen([*cmds],
                        shell=False,
                        stdout=PIPE,
                        stderr=STDOUT, text=True, universal_newlines=True)
        for stdout_line in iter(process.stdout.readlines(), ""):
            yield stdout_line
        process.stdout.close()
        return_code = process.wait()
        if return_code:
            raise CalledProcessError(return_code, cmds)

        if process.returncode != 0:
            logger.warning(
                f"Command returned without returncode 0: {cmds}...{process.returncode}...{process.stdout}")
            return
        return process

    except OSError as e:
        logger.error(f"Failed to execute command: {cmds} {e}")
        return


def run_command_as_user(cmds: list, user: User):
    """Run a command as a specific user using  the subprocess library."""
    try:
        logger.info(f"Executing: {cmds}")
        r = run([*cmds], shell=False,
                capture_output=True, text=True, user=user.get_uid(), group=user.get_gid())

        if r.returncode != 0:
            logger.warning(
                f"Command returned without returncode 0: {cmds}...{r.returncode}")
            return
        return r

    except OSError as e:
        logger.error(f"Failed to execute command: {cmds} {e}")
        return


# TODO: REWORK


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


def test():
    logger.info("Hello Info!")
    logger.error("Hello Error!")
    pass

# def hide_desktop_app(app: str, user: User):
#     '''Hide a desktop app from user so he cannot access via the acitvities screen.'''

#     if not os.path.exists(os.path.normpath(f"{user.home_dir}/.local/share/applications/{app}")):
#         color.print_info(
#             f"The app {app} is not accessible to {user.username}")
#         return
#     make_mutable(os.path.normpath(
#         f"{user.home_dir}/.local/share/applications/{app}"))
#     with open(os.path.normpath(
#             f"{user.home_dir}/.local/share/applications/{app}"), "r+") as f:
#         content = f.read()

#         if "NoDisplay=true" in content:
#             color.print_info(
#                 f"{app} is already hidden from {user.username}")

#         elif "NoDisplay=false" in content:
#             content = content.replace(
#                 "NoDisplay=false", "NoDisplay=true")

#         elif "NoDisplay" not in content:
#             content = content.replace(
#                 "[Desktop Entry]", "[Desktop Entry]\nNoDisplay=true")

#         f.seek(0)
#         f.truncate()
#         f.write(content)

#     make_immutable(os.path.normpath(
#         f"{user.home_dir}/.local/share/applications/{app}"))


# def show_desktop_app(app: str, user: User):
#     '''Show a desktop app to user so he can access via the acitvities screen.'''

#     if not os.path.exists(os.path.normpath(
#             f"{user.home_dir}/.local/share/applications/{app}")):
#         color.print_info(
#             f"The app {app} is not accessible to {user.username}")
#         return
#     make_mutable(os.path.normpath(
#         f"{user.home_dir}/.local/share/applications/{app}"))
#     with open(os.path.normpath(
#             f"{user.home_dir}/.local/share/applications/{app}"), "r+") as f:
#         content = f.read()

#         if "NoDisplay=false" in content:
#             color.print_info(
#                 f"{app} is already visible for {user.username}")

#         elif "NoDisplay=true" in content:
#             content = content.replace(
#                 "NoDisplay=true", "NoDisplay=false")

#         elif "NoDisplay" not in content:
#             content = content.replace(
#                 "[Desktop Entry]", "[Desktop Entry]\nNoDisplay=false")

#         f.seek(0)
#         f.truncate()
#         f.write(content)

#     make_immutable(os.path.normpath(
#         f"{user.home_dir}/.local/share/applications/{app}"))
