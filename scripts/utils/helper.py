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


def set_hostname(hostname: str):
    """Set the hostname of the system."""

    try:
        with open("/etc/hostname", "w") as f:
            f.write(hostname + "\n")
        logger.info(f"Hostname set to {hostname}")
    except Exception as e:
        logger.error(f"Error setting hostname: {e}")


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
            print("\n")
            return input1
        else:
            print("Your inputs do not match. Please try again.\n")
