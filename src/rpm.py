# Copyright 1999 - 2024. WebPros International GmbH. All rights reserved.
import itertools
import os
import shutil
import subprocess
import typing

from . import files, util, log

REPO_HEAD_WITH_URL = """[{id}]
name={name}
baseurl={url}
"""

REPO_HEAD_WITH_METALINK = """[{id}]
name={name}
metalink={url}
"""


def extract_repodata(repofile: str) -> typing.Iterable[typing.Tuple[str, str, str, str, typing.List[str]]]:
    id = None
    name = None
    url = None
    metalink = None
    additional = []

    with open(repofile, "r") as repo:
        for line in repo.readlines():
            if line.startswith("["):
                if id is not None:
                    yield (id, name, url, metalink, additional)

                id = None
                name = None
                url = None
                metalink = None
                additional = []

            log.debug("Repository file line: {line}".format(line=line.rstrip()))
            if line.startswith("["):
                id = line[1:-2]
                continue

            if "=" not in line:
                additional.append(line)
                continue

            field, val = line.split("=", 1)
            field = field.strip().rstrip()
            val = val.strip().rstrip()
            if field == "name":
                name = val
            elif field == "baseurl":
                url = val
            elif field == "metalink":
                metalink = val
            else:
                additional.append(line)

    yield (id, name, url, metalink, additional)


def write_repodata(repofile: str, id: str, name: str, url: str, metalink: str, additional: typing.List[str]) -> None:
    repo_format = REPO_HEAD_WITH_URL
    if url is None:
        url = metalink
        repo_format = REPO_HEAD_WITH_METALINK

    with open(repofile, "a") as dst:
        dst.write(repo_format.format(id=id, name=name, url=url))
        for line in additional:
            dst.write(line)


def remove_repositories(repofile: str, conditions: typing.Callable[[str, str, str, str], bool]) -> None:
    for id, name, url, metalink, additional_lines in extract_repodata(repofile):
        remove = False
        for condition in conditions:
            if condition(id, name, url, metalink):
                remove = True
                break

        if not remove:
            write_repodata(repofile + ".next", id, name, url, metalink, additional_lines)

    if os.path.exists(repofile + ".next"):
        shutil.move(repofile + ".next", repofile)
    else:
        os.remove(repofile)


def filter_installed_packages(lookup_pkgs: typing.List[str]) -> typing.List[str]:
    return [pkg for pkg in lookup_pkgs if is_package_installed(pkg)]


def is_package_installed(pkg: str) -> bool:
    res = subprocess.run(["/usr/bin/rpm", "--quiet", "--query", pkg])
    return res.returncode == 0


def install_packages(pkgs: str, repository: str = None, force_package_config: bool = False) -> None:
    # force_package_config is not supported yet
    if len(pkgs) == 0:
        return

    command = ["/usr/bin/yum", "install"]
    if repository is not None:
        command += ["--repo", repository]
    command += ["-y"] + pkgs

    util.logged_check_call(command)


def remove_packages(pkgs: str) -> None:
    if len(pkgs) == 0:
        return

    if os.path.exists("/usr/bin/package-cleanup"):
        duplicates = subprocess.check_output(["/usr/bin/package-cleanup", "--dupes"], universal_newlines=True).splitlines()
        for duplicate, pkg in itertools.product(duplicates, pkgs):
            if pkg in duplicate:
                util.logged_check_call(["/usr/bin/rpm", "-e", "--nodeps", duplicate])
                # Since we removed each duplicate, we don't need to remove the package in the end.
                if pkg in pkgs:
                    pkgs.remove(pkg)

    util.logged_check_call(["/usr/bin/rpm", "-e", "--nodeps"] + pkgs)


def handle_rpmnew(original_path: str) -> bool:
    if not os.path.exists(original_path + ".rpmnew"):
        return False

    if os.path.exists(original_path):
        log.debug("The '{path}' file has a '.rpmnew' analogue file. Going to replace the file with this rpmnew file. "
                  "The file itself will be saved as .rpmsave".format(path=original_path))
        shutil.move(original_path, original_path + ".rpmsave")
    else:
        log.debug("The '{path}' file is missing, but has '.rpmnew' analogue file. Going to use it".format(path=original_path))

    shutil.move(original_path + ".rpmnew", original_path)

    return True


def handle_all_rpmnew_files(directory: str) -> None:
    fixed_list = []
    for file in files.find_files_case_insensitive(directory, ["*.rpmnew"]):
        original_file = file[:-len(".rpmnew")]
        if handle_rpmnew(original_file):
            fixed_list.append(original_file)

    return fixed_list


def find_related_repofiles(repository_file: str) -> typing.List[str]:
    return files.find_files_case_insensitive("/etc/yum.repos.d", repository_file)


def update_package_list() -> None:
    util.logged_check_call(["/usr/bin/yum", "update", "-y"])


def upgrade_packages(pkgs: typing.List[str] = None) -> None:
    if pkgs is None:
        pkgs = []

    util.logged_check_call(["/usr/bin/yum", "upgrade", "-y"] + pkgs)


def autoremove_outdated_packages() -> None:
    util.logged_check_call(["/usr/bin/yum", "autoremove", "-y"])
