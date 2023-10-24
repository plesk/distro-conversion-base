# Copyright 1999 - 2023. Plesk International GmbH. All rights reserved.
from enum import Enum, auto
import sys
if sys.version_info < (3, 8):
    import platform


class Distro(Enum):
    unknown = auto()
    unsupported = auto()
    centos7 = auto()
    almalinux8 = auto()
    ubuntu18 = auto()
    ubuntu20 = auto()


DISTRO_MAPPING = {
    "CentOS Linux 7": Distro.centos7,
    "AlmaLinux 8": Distro.almalinux8,
    "Ubuntu 18": Distro.ubuntu18,
    "Ubuntu 20": Distro.ubuntu20,
}


def _parce_os_relase():
    name = ""
    version = ""
    with open("/etc/os-release") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("NAME="):
                name = line.split("=")[1].strip().strip('"')
            elif line.startswith("VERSION_ID="):
                version = line.split("=")[1].strip().strip('"')

    return name, version


def get_distro() -> Distro:
    if hasattr(get_distro, "cache"):
        return get_distro.cache

    if sys.version_info < (3, 8):
        distro = platform.linux_distribution()
    else:
        distro = _parce_os_relase()

    name = distro[0]
    major_version = distro[1].split(".")[0]

    get_distro.cache = DISTRO_MAPPING.get(f"{name} {major_version}", Distro.unknown)

    return get_distro.cache


def get_distro_description(distro: Distro) -> str:
    for key, value in DISTRO_MAPPING.items():
        if value == distro:
            return key

    if distro == Distro.centos7:
        return "CentOS 7"
    elif distro == Distro.almalinux8:
        return "AlmaLinux 8"
    elif distro == Distro.ubuntu18:
        return "Ubuntu 18"
    elif distro == Distro.ubuntu20:
        return "Ubuntu 20"
    else:
        return "Unknown"


def _is_deb_based(distro: Distro) -> bool:
    return distro in [Distro.ubuntu18, Distro.ubuntu20]


def _is_rhel_based(distro: Distro) -> bool:
    return distro in [Distro.centos7, Distro.almalinux8]
