import pwd

def user_exists(username: str) -> bool:
    """Check if a user exists."""
    try:
        pwd.getpwnam(username)  # type: ignore
        return True
    except KeyError:
        return False