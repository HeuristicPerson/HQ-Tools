"""
Library to launch Linux commands through the console. I don't know how difficult could it be to make this library work
with Windows as well.
"""

import subprocess


def execute(pu_command):
    """
    Function to execute a command through the Linux console.

    :param pu_command: The command to execute. i.e. "ls -lah /home/john"

    :return: A keyed dictionary containing two strings with the standard output and the error output.
    """

    u_command_line = pu_command.encode('utf8')
    o_process = subprocess.Popen(u_command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    u_stdout, u_stderr = o_process.communicate()

    u_stdout = u_stdout.decode('utf8')
    u_stderr = u_stderr.decode('utf8')

    return {'u_stdout': u_stdout, 'u_stderr': u_stderr}
