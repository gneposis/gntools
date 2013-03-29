"""
Module for managing gntools .dic (dictionary) file format.
Usage: File(dict_file)
       File(dict_file, types=(str, int))
          - Keys are strings, values are integers
       File(dict_file, separator=';')
          - Separator is ';' instead of tab. 

    DIC file format:
      - The first line contains the types of the keys and values separated
        by a tab by default. Empty string there indicates default type
        identification. That means we try to convert the corresponding
        string to integer or float, and if that fails, we leave it as
        string.

      - From that on each line contains a key, value pair separated by a
        tab by default.

      - Examples ('N|' for line number, <-...-> is tab, '...' for missing
        parts):

          1|int<--->str       1|<------>str       1|
          2|1<----->T-34      2|1<----->T-34      2|1<----->T-34
             ...                 ...                 ...
         62|2865<-->110      62|2865<-->110      62|2865<-->110

        Here in the first example all keys are integers and all values are
        strings. Personally, I prefer to declare types explicitely, since
        as you can see, in line 62 there is a tank name which would be
        converted to integer by default which would mess up our value
        types. Second example results the same as first one if all keys
        are integers. Third however defines default mechanism for both
        keys and values (in this case, a tab in first line is optional),
        so T-34 becames a string but 110 will be converted to integer.
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

SEPARATOR = '\t'

class TypeNotValidError(Exception): pass

class File(gntools.formats.File):
    def __init__(self, path, separator=SEPARATOR):
        super().__init__(path)
        self.version = None

        types, data = self.read()

        self.obj = dict()
     
        for row in data.splitlines():
            key_, value_ = row.split(SEPARATOR)
     
            if not types[0]:
                key = deftype(key_.strip())
            else:
                key = types[0](key_.strip())
            if not types[1]:
                value = deftype(value_)
            else:
                value = types[1](value_)
     
            self.obj.update({key: value})


    def read(self):
        with open(self.fullpath) as f:
            keytype, valuetype = [str2type(t.strip())
                                   for t in f.readline().split(SEPARATOR)]
            r = f.read()
        return (keytype, valuetype), r

if __name__ == '__main__':
    pass