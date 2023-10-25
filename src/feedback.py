# Copyright 1999 - 2023. Plesk International GmbH. All rights reserved.

import os
import subprocess
import typing
import zipfile

from . import dist


class Feedback():
    VERSIONS_FILE_PATH = "versions.txt"

    def __init__(self, util_name: str, util_version: str,
                 filelist: typing.List[str] = None, collect_actions: typing.List[typing.Callable] = None) -> None:
        self.util_name = util_name
        self.util_version = util_version

        if filelist is None:
            filelist = []
        self.keep_files = filelist

        if collect_actions is None:
            collect_actions = []

        self.created_files = [self.VERSIONS_FILE_PATH]
        for action in collect_actions:
            self.created_files.append(action())

        self._prepare_versions_file()

    def _prepare_versions_file(self):
        with open(self.VERSIONS_FILE_PATH, "w") as versions:
            try:
                versions.write("The {utility} utility version: {ver}\n".format(utility=self.util_name, ver=self.util_version))
                versions.write("Distribution information: {}\n".format(dist.get_distro_description(dist.get_distro())))

                try:
                    uname_path = "/usr/bin/uname"
                    if not os.path.exists(uname_path):
                        uname_path = "/bin/uname"

                    kernel_info = subprocess.check_output([uname_path, "-a"], universal_newlines=True).splitlines()[0]
                except FileNotFoundError:
                    kernel_info = "not available. likely we are in a container"

                versions.write("Kernel information: {}\n".format(kernel_info))
            except subprocess.CalledProcessError:
                versions.write("Plesk version is not available\n")

    def save_archive(self, archive_name: str):
        with zipfile.ZipFile(archive_name, "w") as zip_file:
            files_to_store = self.keep_files + self.created_files
            for file in (file for file in files_to_store if os.path.exists(file)):
                zip_file.write(file)

    def __del__(self):
        for file in self.created_files:
            if os.path.exists(file):
                os.unlink(file)
