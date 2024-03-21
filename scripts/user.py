from crypt import crypt  # type: ignore
import os
import pwd
import subprocess

from custom_logger import logger
from utils.usr_helper import user_exists


class User():
    """Class to represent a user on a Unix System."""

    def __init__(self, username: str, password: str, desktop_entries: list, sudo: bool = False) -> None:
        self.username = username
        self.password = password
        self.sudo = sudo
        self.desktop_entries = desktop_entries
        self.__load_data()
        # self.__fill_home()

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
