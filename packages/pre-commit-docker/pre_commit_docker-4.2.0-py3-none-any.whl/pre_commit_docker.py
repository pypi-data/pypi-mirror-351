import os
import socket
import re

import pre_commit.languages.docker


def _is_in_docker() -> bool:
    try:
        with open("/proc/1/cgroup", "rb") as f:
            if b"docker" in f.read():
                return True
    except FileNotFoundError:
        pass
    return os.path.exists("/.dockerenv")


pre_commit.languages.docker._is_in_docker = _is_in_docker


def _get_container_id() -> str:
    with open("/proc/1/cgroup", "rb") as f:
        for line in f.readlines():
            if line.split(b":")[1] == b"cpuset":
                return os.path.basename(line.split(b":")[2]).strip().decode()
    hostname = socket.gethostname()
    if re.match(r"^[0-9a-f]{12}$", hostname):
        return hostname
    raise RuntimeError("Failed to find the container ID in /proc/1/cgroup.")


pre_commit.languages.docker._get_container_id = _get_container_id


def main() -> int:
    from pre_commit.main import main

    return main()
