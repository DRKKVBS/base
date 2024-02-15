import os
import subprocess
from custom_logger import logger


def install_package(package_name: str):
    """Install a package using apt."""

    logger.info(f"Installing {package_name}")

    if apt_installed(package_name) or snap_installed(package_name):
        logger.debug(f"\t Skipping {package_name}. It is already installed")
        return
    subprocess.run(["apt", "install", "-y", package_name], check=True)


def install_file(path: str):
    """Install a package from file."""

    package_name = os.path.split(path)[1].split("_")[0]

    logger.info(f"Installing {package_name}")

    if apt_installed(package_name) or snap_installed(package_name):
        logger.debug(f"\t Skipping {package_name}. It is already installed")
        return
    subprocess.run(["apt", "install", "-y", path], check=True)


def remove_package(package_name: str):
    """Remove a package from the system."""

    logger.info(f"Removing {package_name}")

    if apt_installed(package_name):
        subprocess.run(["apt", "autoremove", "-y", package_name], check=True)

    elif snap_installed(package_name):
        subprocess.run(["snap", "remove", "-y", package_name], check=True)

    else:
        logger.debug(f"\t Skipping {package_name}. It is not installed")
        return


def snap_installed(package_name: str):
    """Check if a package is installed via snap."""

    process = subprocess.run(["snap", "list", package_name])
    return True if process.returncode == 0 else False


def apt_installed(package_name: str):
    """Check if a package is installed."""

    process = subprocess.run(
        ["apt", "list", "--installed", package_name])

    return True if process.stdout != None and package_name in process.stdout.decode() else False


def update_package_db():
    """Update the system package database."""
    subprocess.run(["apt", "update"], check=True)


def upgrade_pkgs():
    """Upgrade all packages on the system."""
    subprocess.run(["apt", "upgrade", "-y"], check=True)
