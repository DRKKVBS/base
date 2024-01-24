import os
import pwd
import subprocess
import crypt
import utils
import custom_logger


class User():
    """Class to represent a user on a Unix System."""

    def __init__(self, username: str, password: str, sudo: bool, desktop_entries: list) -> None:
        self.username = username
        self.password = password
        self.sudo = sudo
        self.desktop_entries = desktop_entries
        self.logger = custom_logger.setup_logging()
        self.create_user()

    def create_user(self):
        """Create a user."""

        self.logger.info(f"Creating user {self.username}")

        # Check if user exists
        if self.user_exists():
            self.get_user_data()
            self.logger.info(
                f"Skipping User Creationt, {self.username} already exists!")
            return

        cmd = ["useradd", "-m", "-s", "/bin/bash"]

        # Add user to the sudo group
        if self.sudo == True:
            self.logger.info(f"Adding {self.username} to the sudo group")
            cmd.append("-G")
            cmd.append("sudo")

        # Set the user password
        self.logger.info(f"Setting user password")
        cmd.append("-p")
        cmd.append(crypt.crypt(self.password))  # type: ignore

        # Create user
        try:
            subprocess.run([*cmd, self.username])

            if self.password == "":
                subprocess.run(["passwd", "-d", self.username])

        except Exception as e:
            self.logger.error(f"Error creating user {self.username}: {e}")

        else:
            self.get_user_data()
            self.create_home_dir()

    def user_exists(self) -> bool:
        """Check if a user exists."""
        try:
            pwd.getpwnam(self.username)  # type: ignore
            return True
        except KeyError:
            return False

    def create_home_dir(self):
        """Create the home directory of the user."""

        for dir in ["/.config/", "/.local/", "/.local/share/applications/"]:

            # Create home directory
            try:
                os.makedirs(
                    os.path.normpath(
                        f"{self.__home_dir}/{dir}"), exist_ok=True)
                self.run_command(
                    ["chown", "-R", f"{self.__uid}:{self.__gid}", dir])

            except Exception as e:
                print("Failed to create home directory: %s" % e)

    def get_user_data(self):
        """Get system data of the user"""

        # Get system data of the user
        user = pwd.getpwnam(self.username)  # type: ignore
        self.__uid = user.pw_uid
        self.__gid = user.pw_gid
        self.__home_dir = user.pw_dir
        print(user)
        print(self.__home_dir)

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
            self.logger.info(f"Executing: {cmds}")
            r = subprocess.run([*cmds], shell=False,
                               capture_output=True, text=True, user=self.__uid, group=self.__gid)

            if r.returncode != 0:
                self.logger.warning(
                    f"Command returned without returncode 0: {cmds}...{r.returncode}")
                return
            return r

        except OSError as e:
            self.logger.error(f"Failed to execute command: {cmds} {e}")
            return
