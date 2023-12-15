import os
import pwd
import subprocess
from print_colors import Color

color = Color()


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
    color.print_info(f"Changed permissions for {root_path} to {mode}")
    for root, dirs, files in os.walk(root_path):
        color.print_info(f"{root}...{dirs}...{files}")

        # Set perms on sub-directories
        for dir in dirs:

            dir = os.path.join(root, dir)
            os.chown(dir, uid=uid, gid=gid)  # type: ignore
            color.print_info(f"Changed Ownership for {dir} to {uid}:{gid}")
            os.chmod(dir, mode)
            color.print_info(f"Changed permissions for {dir} to {mode}")

        # Set perms on files
        for file in files:
            file = os.path.join(root, file)
            os.chown(file, uid=uid, gid=gid)  # type: ignore
            color.print_info(f"Changed Ownership for {file} to {uid}:{gid}")
            os.chmod(file, mode)
            color.print_info(f"Changed permissions for {file} to {mode}")


def set_hostname(hostname: str):
    """Set the hostname of the system."""

    with open("/etc/hostname", "w") as f:
        color.print_info(f"Changing hostname to {hostname}")
        f.write(hostname)


def install_package(package_name: str, file_path=None):
    """Install a package using apt."""

    if package_is_installed(package_name):
        color.print_info(f"{package_name} already installed")
    else:
        # Install the package from the file if a file path is given
        color.print_info(f"Installing {package_name}")
        package_name = package_name if file_path == None else file_path
        run_command(["apt", "install", "-y", package_name])


def package_is_installed(package_name: str):
    """Check if a package is installed."""

    return True if run_command(["dpkg", "-l", package_name]) != "" else False


def get_uid(user: str):
    """Get the uid of a user."""

    try:
        return pwd.getpwnam(user).pw_uid  # type: ignore
    except KeyError:
        color.print_error(f"User {user} not found!")
        raise


def get_gid(user: str):
    """Get the gid of a user."""

    try:
        return pwd.getpwnam(user).pw_gid  # type: ignore
    except KeyError:
        color.print_error(f"User {user} not found!")
        raise


def get_home_dir(user: str):
    """Get the gid of a user."""

    try:
        return pwd.getpwnam(user).pw_gid  # type: ignore
    except KeyError:
        color.print_error(f"User {user} not found!")
        raise


def set_file_permissions(file_path: str, uid: int, gid: int, mode: int = 0o644):
    """Set the file permissions of a file."""
    try:
        color.print_info(f"Set Ownership of {file_path}!")
        os.chown(file_path, uid, gid)  # type: ignore

        color.print_info(f"Set Permissions of {file_path}!")
        os.chmod(file_path, mode)
    except FileNotFoundError as e:
        color.print_error(f"File {file_path} not found!")


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
        color.print_info(f"Executing: {cmds}")
        r = subprocess.run([*cmds], shell=False,
                           capture_output=True, text=True)

        if r.returncode != 0:
            color.print_error(f"Failed to execute command: {cmds}")
            return
        return r

    except OSError as e:
        color.print_error(f"Failed to execute command: {cmds} {e}")
