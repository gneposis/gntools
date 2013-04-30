"""
Module for managing INI file format.
Usage: File(ini_file)

    INI file format:
      - The INI file format is an informal standard for configuration
        files for some platforms or software. INI files are simple text
        files with a basic structure composed of "sections" and
        "properties".
"""

# ini.py by Adam Szieberth (2013)
# Python 3.3.0 (Windows Xp)

# Full license text:
# ------------------------------------------------------------------------
#              DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                        Version 2, December 2004

# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>

# Everyone is permitted to copy and distribute verbatim or modified copies
# of this license document, and changing it is allowed as long as the name
# is changed.

#              DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#    TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

# 0. You just DO WHAT THE FUCK YOU WANT TO.
# ------------------------------------------------------------------------
import configparser
import io
import os
import sys

import gntools.formats

DEFAULT_ENCODING = 'cp1250'

class File(gntools.formats.File):
    def __init__(self, path):
        super().__init__(path)

        self.obj = configparser.ConfigParser()

        try:
            data = self.load()
        except:
            with open(self.fullpath) as f:
                self.obj.read_file(f)
        else:
            self.obj.readfp(data)


    def load(self):
        io_obj = io.StringIO()
        with open(self.fullpath) as f:
            io_obj.write(f.read().encode(DEFAULT_ENCODING).decode())
        io_obj.seek(0)
        # For the case of getting an UTF-8Y flag
        if io_obj.read(1) != '\ufeff':
            io_obj.seek(0)
        return io_obj


if __name__ == '__main__':
    pass