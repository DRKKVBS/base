import grp
import logging
import os
import pwd
import subprocess
import sys
import apt  # type: ignore


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


def create_dir_not_exists(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def set_hostname(hostname: str):
    """Set the hostname of the system."""

    with open("/etc/hostname", "w") as f:
        f.write(hostname)


def install_package(package_name: str):
    """Install a package using apt."""

    cache = apt.cache
    cache.update()
    cache.Cache()
    cache.open()

    pkg = cache[package_name]
    if pkg.is_installed:
        print(f"{package_name} already installed".format(pkg_name=package_name))
    else:
        pkg.mark_install()

        try:
            cache.commit()
        except Exception as arg:
            print("Sorry, package installation failed [{err}]".format(
                err=str(arg)), file=sys.stderr)


def get_uid(user: str):
    """Get the uid of a user."""

    try:
        return pwd.getpwnam(user).pw_uid  # type: ignore
    except KeyError:
        print(f"User {user} not found!", file=sys.stderr)
        raise


def get_gid(user: str):
    """Get the gid of a user."""

    try:
        return pwd.getpwnam(user).pw_gid  # type: ignore
    except KeyError:
        print(f"User {user} not found!", file=sys.stderr)
        raise


def get_home_dir(user: str):
    """Get the gid of a user."""

    try:
        return pwd.getpwnam(user).pw_gid  # type: ignore
    except KeyError:
        print(f"User {user} not found!", file=sys.stderr)
        raise


def run_command(cmds: list, uid=None, gid=None):
    """Run a command as a specific user."""

    logging.info("Execute command: %s" % cmds)

    try:
        r = subprocess.run([*cmds], shell=False)
        # return r

    except Exception as e:
        logging.error("Failed to execute command: ", cmds, e)


def set_file_permissions(file_path: str, uid: int, gid: int, mode: int = 0o644):
    """Set the file permissions of a file."""
    try:
        os.chown(file_path, uid, gid)  # type: ignore
        os.chmod(file_path, mode)
    except FileNotFoundError as e:
        print(f"File {file_path} not found!", file=sys.stderr)


def make_immutable(path: str):
    '''Make a file or a directory immutable using Chattr.'''

    path = os.path.normpath(path)
    run_command(["chattr", "+i", path])


def make_mutable(path: str):
    '''Make a file or a directory mutable using Chattr.'''

    path = os.path.normpath(path)
    run_command(["chattr", "-i", path])
