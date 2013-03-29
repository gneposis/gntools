"""
Module for managing gntools .lst (list) file format.
Usage: File(lst_file)

    LST file format:
      - First line contains the type of the column data (float, int,
        str). Empty string there indicates default type identification.
        That means we try to convert the corresponding string to integer
        or float, and if that fails, we leave it as string.

      - After this, list elements, one per line.
"""

# dic.py by Adam Szieberth (2013)
# Python 3.3.0 (Arch Linux)

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
import gntools.formats

from gntools.core.types import deftype, str2type

class File(gntools.formats.File):
    def __init__(self, path):
        super().__init__(path)

        type_, data = self.read()

        self.obj = [d.strip() for d in data.splitlines()] 

    def read(self):
        with open(self.fullpath) as f:
            type_ = str2type(f.readline().strip())
            r = f.read()
        return type, r

    def __getitem__(self, i):
        return self.obj[i]

if __name__ == '__main__':
    pass