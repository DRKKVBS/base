from utils.helper import run_command
from custom_logger import logger

def install_package(package_name: str):
    """Install a package using apt."""

    logger.info(f"Installing {package_name}")

    if package_is_installed(package_name):
        logger.debug(f"\t Skipping {package_name}. It is already installed")
        return
    run_command(["apt", "install", "-y", package_name])


def remove_package(package_name: str):
    """Remove a package from the system."""
    pass

def snap_installed(package_name: str):
    """Check if a package is installed via snap."""

    return True if run_command(["snap", "list", package_name]) != None else False

def package_is_installed(package_name: str):
    """Check if a package is installed."""

    return True if run_command(["dpkg", "-l", package_name]) != None else False