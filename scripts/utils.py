from os import makedirs, chmod, listdir, path
from os.path import normpath, realpath, dirname
import shutil
from subprocess import PIPE, STDOUT, Popen, run
import sys

from user import User
from custom_logger import logger


def get_root_dir():
    """Get the root directory of the project."""
    return realpath(dirname(__file__)).split('scripts')[0]


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


def install_package(package_name: str, file_path=None):
    """Install a package using apt."""

    logger.info(f"Installing {package_name}")

    if package_is_installed(package_name):
        logger.debug(f"\t Skipping {package_name}. It is already installed")
    else:

        # Install the package from the file if a file path is given
        package_name = package_name if file_path == None else file_path
        run_command(["apt", "install", "-y", package_name])


def package_is_installed(package_name: str):
    """Check if a package is installed."""

    return True if run_command(["dpkg", "-l", package_name]) != None else False


def set_file_permissions(file_path: str, uid: int, gid: int, mode: int = 0o644):
    """Set the file permissions of a file."""
    file_path = normpath(file_path)
    try:
        logger.info(f"Set Ownership of {file_path}!")
        shutil.chown(file_path, uid, gid)  # type: ignore

        logger.info(f"Set Permissions of {file_path}!")
        chmod(file_path, mode)
    except FileNotFoundError as e:
        logger.error(f"File {file_path} not found!")


def make_immutable(path: str):
    '''Make a file or a directory immutable using Chattr.'''

    path = normpath(path)
    run_command(["chattr", "+i", path])


def make_mutable(path: str):
    '''Make a file or a directory mutable using Chattr.'''

    path = normpath(path)
    run_command(["chattr", "-i", path])


def run_command(cmds: list):
    """Run a command using  the subprocess library."""

    try:
        logger.info(f"subprocess: {cmds}")

        process = Popen(cmds,
                        shell=False,
                        stdout=PIPE,
                        stderr=STDOUT, text=True, universal_newlines=True)
        for stdout_line in iter(process.stdout.readline, ""):
            print(stdout_line, end="")
        process.stdout.close()
        return_code = process.wait()

        if process.returncode:
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

    applications_path = normpath(
        f"{user.get_home_dir()}/.local/share/applications/")

    for app in listdir("/usr/share/applications/"):

        if app.endswith(".desktop") and app not in listdir(applications_path):
            shutil.copyfile(normpath(
                f"/usr/share/applications/{app}"), normpath(f"{applications_path}/{app}"))

        shutil.chown(normpath(
            f"{applications_path}/{app}"), user.get_uid(), user.get_gid())

    for app in listdir(applications_path):

        if app in visible_apps:
            with open(normpath(f"{applications_path}/{app}"), "r+") as f:
                text = f.read()
                if "NoDisplay=True" in text:
                    text.replace("NoDisplay=True", "NoDisplay=False")
                elif "NoDisplay=False" in text:
                    break
                elif "NoDisplay" not in text:
                    text.replace("[Desktop Entry]",
                                 "[Desktop Entry]\nNoDisplay=False")
        else:
            with open(normpath(f"{applications_path}/{app}"), "r+") as f:
                text = f.read()
                if "NoDisplay=True" in text:
                    break
                elif "NoDisplay=False" in text:
                    text.replace("NoDisplay=False", "NoDisplay=True")

                elif "NoDisplay" not in text:
                    text.replace("[Desktop Entry]",
                                 "[Desktop Entry]\nNoDisplay=True")


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write(
                "Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def input_validation(question: str):
    """Ask a for input via input() and return their answer. The user has to enter the same input again to confirm.

    "question" is a string that is presented to the user.
    """

    while True:
        input1 = input(question+"\n")
        input2 = input("Please confirm and reenter your input:\n")
        if input1 == input2:
            return input1
        else:
            print("Your inputs do not match. Please try again.\n")

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
