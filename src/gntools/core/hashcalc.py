"""
Module for calculate various hash values (currently only MD5).
Usage: md5f(filename)
       md5(data)
"""

# md5.py by Adam Szieberth (2013)
# Python 3.3 (Arch Linux)

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
import hashlib
from functools import partial

def md5f(filename):
    """
    Returns the md5sum of a given file.
    Usage: md5sum(filename)
    """
    # used code from http://stackoverflow.com/a/7829658
    # by Raymond Hettinger and J.F. Sebastian
    # Guys, if you disagree with my licensing, please contact me! 
    # --------------------------------------------------------------------
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()

def md5(data):
    """Returns the md5sum of a given data."""
    d = md5()
    d.update(data.encode('utf-8'))
    return d.hexdigest()
