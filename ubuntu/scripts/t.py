from subprocess import PIPE, STDOUT, Popen, run

# -*- coding: utf-8 -*-
"""
A convenience module for shelling out with realtime output
includes: 
- subprocess - Works with additional processes.
- shlex - Lexical analysis of shell-style syntaxes.
"""

import subprocess
import shlex


def run(command):
    process = Popen(command, stdout=PIPE, shell=True)
    while True:
        line = process.stdout.readline().rstrip()
        if not line:
            break
        yield line.decode('utf-8')

def run_command(command):
    process = Popen(shlex.split(command), stdout=PIPE)
    while True:
        output = process.stdout.readline().rstrip().decode('utf-8')
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    rc = process.poll()
    return rc

if __name__ == "__main__":
    for path in run("ping -c 5 google.com"):
        print path