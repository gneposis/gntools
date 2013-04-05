"""
Module for path manipulation.
"""

# path.py by Adam Szieberth (2013)
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
import os

def mloc(*args):
    """
    Returns the path defined by args relative to the first argument's
    dirname. It uses os.join to get to the final path.

    Useful to access relative paths from an imported module.
    """
    arguments = [os.path.normpath(p) for p in args]
    arguments[0] = os.path.dirname(arguments[0])
    return os.path.join(*arguments)