# Copyright 1999 - 2023. Plesk International GmbH. All rights reserved.

import os
import subprocess
import typing

from . import log

CONVERTER_TEMP_DIRECTORY = "/usr/local/psa/var/centos2alma"


def send_error_report(error_message: str) -> None:
    # Todo. For now we works only on RHEL-based distros, so the path
    # to the send-error-report utility will be the same.
    # But if we will support Debian-based we should choose path carefully
    send_error_path = "/usr/local/psa/admin/bin/send-error-report"
    try:
        if os.path.exists(send_error_path):
            subprocess.run([send_error_path, "backend"], input=error_message.encode(),
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        # We don't care about errors to avoid mislead of the user
        pass


def get_plesk_version() -> typing.List[str]:
    version_info = subprocess.check_output(["/usr/sbin/plesk", "version"], universal_newlines=True).splitlines()
    for line in version_info:
        if line.startswith("Product version"):
            version = line.split()[-1]
            return version.split(".")

    raise Exception("Unable to parce plesk version output.")


def get_plesk_full_version() -> typing.List[str]:
    return subprocess.check_output(["/usr/sbin/plesk", "version"], universal_newlines=True).splitlines()


_STATUS_FLAG_FILE_PATH = CONVERTER_TEMP_DIRECTORY + "/distupgrade-conversion.flag"


def prepare_conversion_flag() -> None:
    with open(_STATUS_FLAG_FILE_PATH, "w"):
        pass


def send_conversion_status(succeed: bool) -> str:
    results_sander_path = None
    for path in ["/var/cache/parallels_installer/report-update", "/root/parallels/report-update"]:
        if os.path.exists(path):
            results_sander_path = path
            break

    # For now we are not going to install sender in scoupe of conversion.
    # So if we have one, use it. If not, just skip send the results
    if results_sander_path is None:
        log.warn("Unable to find report-update utility. Skip sending conversion status")
        return

    if not os.path.exists(_STATUS_FLAG_FILE_PATH):
        log.warn("Conversion status flag file does not exist. Skip sending conversion status")
        return

    plesk_version = ".".join(get_plesk_version())

    try:
        log.debug("Trying to send status of conversion by report-update utility")
        subprocess.run(["/usr/bin/python3", results_sander_path, "--op", "dist-upgrade", "--rc", "0" if succeed else "1",
                        "--start-flag", _STATUS_FLAG_FILE_PATH, "--from", plesk_version, "--to", plesk_version],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as ex:
        log.warn("Unable to send conversion status: {}".format(ex))

    # usually the file should be removed by report-update utility
    # but if it will be failed, we should remove it manually
    remove_conversion_flag()


def remove_conversion_flag() -> str:
    if os.path.exists(_STATUS_FLAG_FILE_PATH):
        os.unlink(_STATUS_FLAG_FILE_PATH)
