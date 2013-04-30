"""
Module for managing nested dictionary collections.
"""

# nested.py by Adam Szieberth (2013)
# Python 3.3

# Full license text:
# ------------------------------------------------------------------------
#              DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                        Version 2, December 2004
#
# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>
#
# Everyone is permitted to copy and distribute verbatim or modified copies
# of this license document, and changing it is allowed as long as the name
# is changed.
#
#              DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#    TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
# 0. You just DO WHAT THE FUCK YOU WANT TO.
# ------------------------------------------------------------------------

class NestedDict(dict):
    """
    Class for managing nested dictionary structures. Normally, it works
    like a builtin dictionary. However, if it gets a list as an argument,
    it will iterate through that list assuming all elements of that list
    as a key for next level.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, *args):
        if isinstance(args[0], list):
            item = super().__getitem__(args[0][0])
            if isinstance(item, NestedDict) and len(args[0]) > 1:
                return item.__getitem__(args[0][1:])
            else:
                return item
        return super().__getitem__(*args)

    def __setitem__(self, *args):
        if isinstance(args[0], list):
            if len(args[0]) == 1:
                super().__setitem__(args[0][0], args[1])
            else:
                try:
                    item = self.__getitem__(args[0][0])
                except KeyError:
                    super().__setitem__(args[0][0], NestedDict())
                    item = self.__getitem__(args[0][0])
                if len(args[0]) > 2:
                    item.__setitem__(args[0][1:], args[1])
                elif len(args[0]) == 2:
                    item.__setitem__(args[0][1], args[1])
        else:
            super().__setitem__(*args)

    def leafage(self, past_keys=[]):
        """
        Generator to iterate through branches. Used by merge function, but
        can be useful for other object management stuffs.
        """
        for key in self.keys():
            keys = past_keys + [key]
            if not isinstance(self[key], NestedDict):
                yield keys
            else:
                yield from self[key].leafage(past_keys=keys)

    def merge(self, other_nesteddict, func_if_overwrite=None):
        """
        Merges one NestedDict with another. You can control how
        overwriting should be done which is off by default. By setting
        func_if_overwrite to True, overwriting becomes enabled.
        Moreover you can pass a function to it which will be called with
        the list of keys, self, other_nesteddict arguments and expected
        to return True or False.
        """
        for b in other_nesteddict.leafage():
            try:
                self[b]
            except KeyError:
                self[b] = other_nesteddict[b]
            else:
                if self[b] != other_nesteddict[b]:
                    if hasattr(func_if_overwrite, '__call__'):
                        ow = func_if_overwrite(b, self, other_nesteddict)
                    else:
                        ow = func_if_overwrite
                    if ow:
                        self[b] = other_nesteddict[b]

if __name__ == '__main__':
    import pprint

    new_data =[(['new jersey', 'mercer county', 'plumbers'], 3),
               (['new jersey', 'mercer county', 'programmers'], 81),
               (['new jersey', 'middlesex county', 'programmers'], 81),
               (['new jersey', 'middlesex county', 'salesmen'], 62),
               (['new york', 'queens county', 'plumbers'], 9),
               (['new york', 'queens county', 'salesmen'], 36)]

    data = NestedDict()

    for d in new_data:
        data[d[0]] = d[1]

    pprint.PrettyPrinter(indent=0).pprint(data)
