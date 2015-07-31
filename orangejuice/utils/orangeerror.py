#!/usr/bin/env python
# Filename: orangejuice/utils/orangeerror.py


class ConnectError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value
