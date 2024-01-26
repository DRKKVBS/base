import os
import pwd
import subprocess
from crypt import crypt  # type: ignore

from scripts.utils.helper import run_command
from utils.user_helper import user_exists
from custom_logger import logger


class User():
    """Class to represent a user on a Unix System."""

    def __init__(self, username: str, password: str, sudo: bool, desktop_entries: list) -> None:
        self.username = username
        self.password = password
        self.sudo = sudo
        self.desktop_entries = desktop_entries
        self.__create()
        self.__load_data()
        self.__fill_home()

    def __create(self):
        """Create a user."""

        logger.info(f"Creating Account: {self.username}")

        # Check if user exists
        if user_exists(self.username):
            self.__load_data()
            logger.info(
                f"Skipping User Creation, {self.username} already exists!")
            return

        cmd = ["useradd", "-m", "-s", "/bin/bash"]

        # Add user to the sudo group
        if self.sudo == True:
            logger.info(f"Adding {self.username} to the sudo group")
            cmd.append("-G")
            cmd.append("sudo")

        if self.password != None and self.password != "":
            logger.info(f"Setting password")
            cmd.append("-p")
            cmd.append(crypt(self.password))

        # Create user
        logger.info([*cmd, self.username])
        run_command([*cmd, self.username])

        if self.password == None or self.password == "":
            # Remove password
            logger.info(f"Removing password")
            run_command(["passwd", "-d", self.username])

    

    def __fill_home(self):
        """Create the home directory of the user."""
        for dir in ["/.config/", "/.local/share/applications/"]:
            self.run_command(
                ["mkdir", "-p",  os.path.normpath(f"{self.__home_dir}/{dir}")])

    def __load_data(self):
        """Get system data of the user"""

        # Get system data of the user
        user = pwd.getpwnam(self.username)  # type: ignore
        self.__uid = user.pw_uid
        self.__gid = user.pw_gid
        self.__home_dir = user.pw_dir

    def get_uid(self) -> int:
        """Get the uid of a user."""
        return self.__uid

    def get_gid(self) -> int:
        """Get the gid of a user."""
        return self.__gid

    def get_home_dir(self) -> str:
        """Get the home directory of a user."""
        return self.__home_dir

    def run_command(self, cmds: list):
        """Run a command as a specific user using  the subprocess library."""
        try:
            logger.info(f"Executing: {cmds}")
            r = subprocess.run([*cmds], shell=False,
                               capture_output=True, text=True, user=self.__uid, group=self.__gid)

            if r.returncode != 0:
                logger.warning(
                    f"Command returned without returncode 0: {cmds}...{r.returncode}")
                return
            return r

        except OSError as e:
            logger.error(f"Failed to execute command: {cmds} {e}")
            return
