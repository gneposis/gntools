"""
Module for managing built-in types.
"""

# types.py by Adam Szieberth (2013)
# Python 3.3.0 (IDLE), 3.2.2 (Windows)

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
                       
# For some reason __builtins__ is a dictionary here instead of a module.
# Thus we choose a different approach to get builtin classes instead of
# this (use this in interpreter):
# >>> type_ = __builtins__.float
# or this (also works in interpreter:
# >>> type_ = getattr(__builtins__, 'float')
# For builtins we could get our type here like:
# type_ = __builtins__[typestring]
DEF_STR2TYPE_VALIDS = {
                       'float': __builtins__['float'],
                       'int': __builtins__['int'],
                       'str': __builtins__['str'],
                       }

class TypeNotValidError(Exception): pass

def deftype(string):
    """
    Returns the default datatype of a given string.
      - At first, it tries to convert it to float then integer.
      - If fails, returns the string itself.
    """
    if string == '':
        return None
    elif string.find('.') > -1:
        try:
            return float(string)
        except:
            return string
    else:
        try:
            return int(string)
        except:
            return string

def str2type(typestring, valid_types=DEF_STR2TYPE_VALIDS, strict=False):
    """
    Returns a type class of given name string.
    """
    if not typestring and not strict:
        return None
    elif not typestring and strict:
        raise TypeNotValidError(
                       'Empty type string is not allowed in strict mode.')

    if typestring not in valid_types.keys():
        raise TypeNotValidError(
                     'Invalid type {} in type definition, {} was expected'
                     .format(typestring, ' or '.join(valid_types.keys()))) 

    return valid_types[typestring]