# Copyright 1999-2023. Plesk International GmbH. All rights reserved.
# vim:ft=python:

python_library(
    name = 'common.lib',
    srcs = glob(['*.py']),
    visibility = ['PUBLIC'],
)

python_test(
    name = 'libs.tests',
    srcs = glob(['./tests/*.py']),
    deps = [
        ':common.lib',
    ],
    platform = 'py3',
)
