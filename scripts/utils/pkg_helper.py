import os
from custom_logger import logger
from utils.helper import run_command


def install_package(package_name: str):
    """Install a package using apt."""

    logger.info(f"Installing {package_name}")

    if apt_installed(package_name) or snap_installed(package_name):
        logger.debug(f"\t Skipping {package_name}. It is already installed")
        return
    run_command(["apt", "install", "-y", package_name])


def install_file(path: str):
    """Install a package from file."""

    package_name = os.path.split(path)[1].split("_")[0]

    logger.info(f"Installing {package_name}")

    if apt_installed(package_name) or snap_installed(package_name):
        logger.debug(f"\t Skipping {package_name}. It is already installed")
        return
    run_command(["apt", "install", "-y", path])


def remove_package(package_name: str):
    """Remove a package from the system."""

    logger.info(f"Removing {package_name}")

    if apt_installed(package_name):
        run_command(["apt", "autoremove", "-y", package_name])

    elif snap_installed(package_name):
        run_command(["snap", "remove", "-y", package_name])

    else:
        logger.debug(f"\t Skipping {package_name}. It is not installed")
        return


def snap_installed(package_name: str):
    """Check if a package is installed via snap."""

    return True if run_command(["snap", "list", package_name]) != None else False


def apt_installed(package_name: str):
    """Check if a package is installed."""
    output = run_command(["apt", "list", "--installed", package_name])

    return True if output != None and package_name in output else False


def update_package_db():
    """Update the system package database."""
    run_command(["apt", "update"])


def upgrade_pkgs():
    """Upgrade all packages on the system."""
    run_command(["apt", "upgrade", "-y"])
