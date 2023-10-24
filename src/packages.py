# Copyright 1999 - 2023. Plesk International GmbH. All rights reserved.
import typing

from . import dist, dpkg, rpm


def filter_installed_packages(lookup_pkgs: typing.List[str]) -> typing.List[str]:
    return [pkg for pkg in lookup_pkgs if is_package_installed(pkg)]


def is_package_installed(pkg: str) -> bool:
    started_on = dist.get_distro()
    if dist._is_deb_based(started_on):
        return dpkg.is_package_installed(pkg)
    elif dist._is_rhel_based(started_on):
        return rpm.is_package_installed(pkg)
    else:
        raise NotImplementedError(f"Unsupported distro {started_on}")


def install_packages(pkgs: str, repository: str = None, force_package_config: bool = False) -> None:
    started_on = dist.get_distro()
    if dist._is_deb_based(started_on):
        return dpkg.install_packages(pkgs, repository, force_package_config)
    elif dist._is_rhel_based(started_on):
        return rpm.install_packages(pkgs, repository, force_package_config)
    else:
        raise NotImplementedError(f"Unsupported distro {started_on}")


def remove_packages(pkgs: str) -> None:
    started_on = dist.get_distro()
    if dist._is_deb_based(started_on):
        return dpkg.remove_packages(pkgs)
    elif dist._is_rhel_based(started_on):
        return rpm.remove_packages(pkgs)
    else:
        raise NotImplementedError(f"Unsupported distro {started_on}")


def find_related_repofiles(repofiles_mask: str) -> typing.List[str]:
    started_on = dist.get_distro()
    if dist._is_deb_based(started_on):
        return dpkg.find_related_repofiles(repofiles_mask)
    elif dist._is_rhel_based(started_on):
        return rpm.find_related_repofiles(repofiles_mask)
    else:
        raise NotImplementedError(f"Unsupported distro {started_on}")


def update_package_list() -> None:
    started_on = dist.get_distro()
    if dist._is_deb_based(started_on):
        return dpkg.update_package_list()
    elif dist._is_rhel_based(started_on):
        return rpm.update_package_list()
    else:
        raise NotImplementedError(f"Unsupported distro {started_on}")


def upgrade_packages(pkgs: typing.List[str] = None) -> None:
    started_on = dist.get_distro()
    if dist._is_deb_based(started_on):
        return dpkg.upgrade_packages(pkgs)
    elif dist._is_rhel_based(started_on):
        return rpm.upgrade_packages(pkgs)
    else:
        raise NotImplementedError(f"Unsupported distro {started_on}")


def autoremove_outdated_packages() -> None:
    started_on = dist.get_distro()
    if dist._is_deb_based(started_on):
        return dpkg.autoremove_outdated_packages()
    elif dist._is_rhel_based(started_on):
        return rpm.autoremove_outdated_packages()
    else:
        raise NotImplementedError(f"Unsupported distro {started_on}")
