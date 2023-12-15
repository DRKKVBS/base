import os
import pwd
import subprocess
import crypt
import utils


class User():
    """Class to represent a user on a Unix System."""

    def __init__(self, username: str, password: str, sudo: bool, dekstop_entries: list) -> None:
        self.username = username
        self.password = password
        self.sudo = sudo
        self.dekstop_entries = dekstop_entries
        self.create_user()
        self.create_home_dir()

    def create_user(self):
        """Create a user."""

        # Check if user exists
        if self.user_exists():
            self.get_user_data()
            return

        cmd = ["useradd", "-m"]

        # Add user to the sudo group
        if self.sudo == True:
            cmd.append("-G")
            cmd.append("sudo")

        # Set the user password
        if self.password != "":
            cmd.append("-p")
            cmd.append(crypt.crypt(self.password))  # type: ignore

        # Create user
        try:
            subprocess.run([*cmd, self.username])

        except Exception as e:
            print("User Creation failed: %s" % e)

        else:
            self.get_user_data()

    # def set_environment_variables(self):

    def user_exists(self) -> bool:
        """Check if a user exists."""
        try:
            pwd.getpwnam(self.username)  # type: ignore
            return True
        except KeyError:
            return False

    def create_home_dir(self):
        """Create the home directory of the user."""

        # Create home directory
        try:
            path = os.path.normpath(
                f"{self.home_dir}/.local/share/applications/")
            print("Creating home directory for %s" % path)
            os.makedirs(
                path, exist_ok=True)
            utils.chmod_recursive(
                path, 0o755, self.uid, self.gid)
        except Exception as e:
            print("Failed to create home directory: %s" % e)

    def get_user_data(self):
        """Get system data of the user"""

        # Get system data of the user
        user = pwd.getpwnam(self.username)  # type: ignore
        self.uid = user.pw_uid
        self.gid = user.pw_gid
        self.home_dir = user.pw_dir
