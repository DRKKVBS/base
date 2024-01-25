from __future__ import print_function  # Only Python 2.x
import subprocess


def execute(cmd):
    popen = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, universal_newlines=True, text=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        print(stdout_line, end="")
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


# Example
execute(["apt", "update"])
execute(["apt", "upgrade", "-y"])
