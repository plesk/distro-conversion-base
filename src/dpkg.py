# Copyright 1999 - 2024. WebPros International GmbH. All rights reserved.
import os
import subprocess
import typing

from . import files, util

APT_CHOOSE_OLD_FILES_OPTIONS = ['-o', 'Dpkg::Options::=--force-confdef',
                                '-o', 'Dpkg::Options::=--force-confold']


def is_package_installed(pkg: str) -> bool:
    res = subprocess.run(["/usr/bin/dpkg", "-s", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return res.returncode == 0


def install_packages(pkgs: typing.List[str], repository: str = None, force_package_config: bool = False) -> None:
    if len(pkgs) == 0:
        return

    # repository specify is not supported by now
    cmd = ['/usr/bin/apt-get', 'install', '-y']
    if force_package_config is True:
        cmd += APT_CHOOSE_OLD_FILES_OPTIONS
    cmd += pkgs

    util.logged_check_call(cmd, env={"PATH": os.environ["PATH"], "DEBIAN_FRONTEND": "noninteractive"})


def remove_packages(pkgs: typing.List[str]) -> None:
    if len(pkgs) == 0:
        return

    cmd = ["/usr/bin/apt-get", "remove", "-y"] + pkgs
    util.logged_check_call(cmd)


def find_related_repofiles(repository_file: str) -> typing.List[str]:
    return files.find_files_case_insensitive("/etc/apt/sources.list.d", repository_file)


def update_package_list() -> None:
    util.logged_check_call(["/usr/bin/apt-get", "update", "-y"])


def upgrade_packages(pkgs: typing.List[str] = None) -> None:
    if pkgs is None:
        pkgs = []

    cmd = ["/usr/bin/apt-get", "upgrade", "-y"] + APT_CHOOSE_OLD_FILES_OPTIONS + pkgs
    util.logged_check_call(cmd, env={"PATH": os.environ["PATH"], "DEBIAN_FRONTEND": "noninteractive"})


def autoremove_outdated_packages() -> None:
    util.logged_check_call(["/usr/bin/apt-get", "autoremove", "-y"],
                           env={"PATH": os.environ["PATH"], "DEBIAN_FRONTEND": "noninteractive"})


def depconfig_parameter_set(parameter: str, value: str) -> None:
    subprocess.run(["/usr/bin/debconf-communicate"], input=f"SET {parameter} {value}\n",
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, universal_newlines=True)


def depconfig_parameter_get(parameter: str) -> None:
    process = subprocess.run(["/usr/bin/debconf-communicate"], input=f"GET {parameter}\n",
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True, universal_newlines=True)
    return process.stdout.split(" ")[1].strip()


def restore_installation() -> None:
    util.logged_check_call(["/usr/bin/apt-get", "-f", "install", "-y"])


def do_distupgrade() -> None:
    util.logged_check_call(["apt-get", "dist-upgrade", "-y"] + APT_CHOOSE_OLD_FILES_OPTIONS,
                           env={"PATH": os.environ["PATH"], "DEBIAN_FRONTEND": "noninteractive"})