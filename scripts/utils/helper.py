from subprocess import PIPE, STDOUT, Popen, run
import sys

from custom_logger import logger


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


# def run_command_as_user(cmds: list, user: User):
#     """Run a command as a specific user using  the subprocess library."""
#     try:
#         logger.info(f"Executing: {cmds}")
#         r = run([*cmds], shell=False,
#                 capture_output=True, text=True, user=user.get_uid(), group=user.get_gid())

#         if r.returncode != 0:
#             logger.warning(
#                 f"Command returned without returncode 0: {cmds}...{r.returncode}")
#             return
#         return r

#     except OSError as e:
#         logger.error(f"Failed to execute command: {cmds} {e}")
#         return


# TODO: REWORK


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
