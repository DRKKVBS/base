import pwd
import subprocess
import crypt


class User():
    """Class to represent a user on a Unix System."""

    def __init__(self, username: str, password: str, sudo: bool, dekstop_entries: list) -> None:
        self.username = username
        self.password = password
        self.sudo = sudo
        self.dekstop_entries = dekstop_entries
        self.create_user()

    def create_user(self):
        """Create a user."""

        # Check if user exists
        if self.user_exists():
            self.get_user_data()
            return

        # Create user
        try:
            if self.sudo == True:
                subprocess.run(["useradd", "-m", "-G", "sudo",
                               "-p", crypt.crypt(self.password), self.username])
                return

            if self.password == "":
                subprocess.run(["useradd", "-m", self.username])
                return

            subprocess.run(
                ["useradd", "-m", "-p", crypt.crypt(self.password), self.username])

        except Exception as e:
            print("User Creation failed: %s" % e)

        else:
            self.get_user_data()

    def user_exists(self) -> bool:
        """Check if a user exists."""
        try:
            pwd.getpwnam(self.username)  # type: ignore
            return True
        except KeyError:
            return False

    def get_user_data(self):
        """Get system data of the user"""

        # Get system data of the user
        user = pwd.getpwnam(self.username)  # type: ignore
        self.uid = user.pw_uid
        self.gid = user.pw_gid
        self.home_dir = user.pw_dir
