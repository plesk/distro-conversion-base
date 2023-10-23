# Copyright 1999 - 2023. Plesk International GmbH. All rights reserved.
import subprocess
import typing

from . import log


def logged_check_call(cmd: str, **kwargs) -> None:
    log.info("Running: {cmd!s}. Output:".format(cmd=cmd))

    # I beleive we should be able pass argument to the subprocess function
    # from the caller. So we have to inject stdout/stderr/universal_newlines
    kwargs["stdout"] = subprocess.PIPE
    kwargs["stderr"] = subprocess.STDOUT
    kwargs["universal_newlines"] = True

    process = subprocess.Popen(cmd, **kwargs)
    while None is process.poll():
        line = process.stdout.readline()
        if line and line.strip():
            log.info(line.strip(), to_stream=False)

    if process.returncode != 0:
        log.err(f"Command '{cmd}' failed with return code {process.returncode}")
        raise subprocess.CalledProcessError(process.returncode, cmd)

    log.info("Command '{cmd}' finished successfully".format(cmd=cmd))


def merge_dicts_of_lists(dict1: typing.Dict[typing.Any, typing.Any],
                         dict2: typing.Dict[typing.Any, typing.Any]) -> typing.Dict[typing.Any, typing.Any]:
    for key, value in dict2.items():
        if key in dict1:
            for item in value:
                dict1[key].append(item)
        else:
            dict1[key] = value
    return dict1
