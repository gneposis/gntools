"""
Module for manipulating iterable objects.
"""

# iterable.py by Adam Szieberth (2013)
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

def split_by_lenlist(obj, list_of_lengths):
    """Generator to split an indexable object by a list of lengths."""
    class LengthsDontMatchError(Exception): pass
    if len(obj) != sum(list_of_lengths):
        raise LengthsDontMatchError(
            'Lengths do not match: {}!= {}'.format(data, list_of_lengths))
    i = 0
    for item in list_of_lengths:
        yield obj[i:i+item]
        i += item