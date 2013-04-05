"""
Module for manage own collwction types.
"""

# collections.py by Adam Szieberth (2013)
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

def _init_items(*args):
    if len(args) > 1:
        return args
    elif len(args) == 1:
        return args[0]
    else:
        return []

class ListOfClass(list):
    """
    A list which contains elements of a specific class.
    """
    class WrongItemClassError(AttributeError): pass
    class WrongClassTypeError(AttributeError): pass

    def __init__(self, *args, itemclass, parentclass, strict=True):

        if not issubclass(itemclass, parentclass):
            raise self.WrongItemClassError(
                'Unsupported itemclass (not {}): {}'
                .format(parentclass, itemclass))
        self.itemclass = itemclass
        self.parentclass = parentclass
        self.strict = strict

        super().__init__([])

        for i in _init_items(*args):
            self.append(i)

    def checkitemclass(self, classobj):
        if not isinstance(classobj, self.itemclass):
            if self.strict:
                raise self.WrongClassTypeError(
                    'Unsupported type (not {}): {}'
                    .format(self.itemclass, type(classobj)))
            return False
        return True

    def append(self, item):
        check = self.checkitemclass(item)
        if check:
            super().append(item)

    def uniqueattr(self):
        """
        Returns the attributes which are not attributes of the parent
        class.
        """
        magicattr = set(
                        [attr for attr in dir(self.itemclass)
                         if attr.startswith('__') and attr.endswith('__')
                         ])

        diffattr = set(dir(self.itemclass)) - set(dir(self.parentclass))

        return diffattr - magicattr


class DictList(ListOfClass):
    """
    A list which contains dictionaries.

    Also supports for inherited dictionaries as its content, and supports
    filtering by not only by their values but also by their functions.
    """
    class AttrClassIsNotDictError(AttributeError): pass
    class WrongAttrTypeError(AttributeError): pass

    def __init__(self, *args, itemclass=dict, parentclass=dict,
                                                             strict=True):
        super().__init__(*args, itemclass=itemclass,
                                parentclass=parentclass,
                                strict=strict)

    def filt(self, filt_dict):
        """
        Filters items by a dictonary and returns a new DictList.

        Even supports filtering by unique attributes which differs from
        the parent's (usually builtin dict) attributes. This is useful if
        we defined a function in the dictionary class to calculate
        something based on its content and we want to use tis function for
        filtering.

        For example our tank DictList class instance (tankdlist) have
        'countryid': 5 and 'typeid': 4, but it also have functions named
        as self.country() and self.tanktype() to retrieve the string
        representations of the id values, we can use filtering like this:

        >>> tankdlist.filt{'country': 'UK', 'tanktype': 'TD', 'tier': 4}

        Note that the dictionaries have keyes named as tier, so we can mix
        keys and arguments for filtering.
        """
        result = DictList(itemclass=self.itemclass)
        result.__class__ = self.__class__

        for i in self:
            match = True
            for key in filt_dict:
                if key in self.uniqueattr():
                    val = getattr(i, key)()
                else:
                    val = i[key]

                if val == filt_dict[key]:
                    match = match and True
                else:
                    match = False

            if match:
                result.append(i)
        return result

    def report(self, *args, itemclass=list):
        """
        Converts each item to a list which contains the retrieved values
        or results of unique attribute fuctions defined by args and
        fetched by _init_items(*args).
        """
        #TODO: sorting hierarchy

        items = _init_items(*args)
        result = ListList(header=items, itemclass=itemclass)

        for i in self:
            sublist = itemclass()
            for key in items:
                if key in self.uniqueattr():
                    val = getattr(i, key)()
                else:
                    val = i[key]

                sublist.append(val)

            result.append(sublist)

        result.sort()
        return result

class ListList(ListOfClass):
    """
    A list which contains lists.
    """
    def __init__(self, *args,
                       header=None,
                       itemclass=list,
                       parentclass=list,
                       strict=True):

        self.header = header

        super().__init__(*args, itemclass=itemclass,
                                parentclass=parentclass,
                                strict=strict)

class NestedDict(dict):
    """
    Nested dictionary.

    Accepts lists, and use its elements as nested keys.

    Usage:
    >>> d = Dict()
    >>> d[['key1', 'key2', 'key3']] = 'val1'
    >>> d
    {'key1': {'key2': {'key3': 'val1'}}}
    >>> d[['key1', 'key22']] = 'val2'
    >>> d
    {'key1': {'key2': {'key3': 'val1'}, 'key22': 'val2'}}
    >>> d[[10,11]] = 12
    >>> d
    {'key1': {'key2': {'key3': 'val1'}, 'key22': 'val2'}, 10: {11: 12}}
    >>> d['a'] = 'b'
    >>> d
    {'key1': {'key2': {'key3': 'val1'}, 'key22': 'val2'}, 10: {11: 12},
        'a': 'b'}
    """
    def __setitem__(self, *args):
        # __setitem__ also accepts a single None argument which makes no
        # change in the dictionary
        if len(args) == 1 and args[0] is None:
            pass
        elif (len(args) == 2
                    ) and (
                isinstance(args[0], list)
                    ) and (
                len(args[0]) >= 1):
            self._setnesteditem(args, self)
        else:
            super().__setitem__(*args)

    def _setnesteditem(self, setitem_args, current_dict):

        class NotDictionary(Exception): pass
        if not isinstance(current_dict, dict):
            raise NotDictionary(
                    'Dictionary was expected, got {}'
                    .format(type(current_dict))
                )

        keys_ = setitem_args[0]
        first_key = keys_[0]
        value = setitem_args[1]
        next_args = keys_[1:], value

        if not current_dict.__contains__(first_key):
            if len(keys_) > 1:
                current_dict[first_key] = dict()
            elif len(keys_) == 1:
                current_dict[first_key] = value

        if len(keys_) > 1:
            return self._setnesteditem(next_args, current_dict[first_key])


class ItemClock:
    def __init__(self, items, start_ind=0):
        self.items = items
        self.i = start_ind

    def __eq__(self, string):
        if repr(self) == string:
            return True
        else:
            return False

    def __iadd__(self, count):
        current_i = self.i
        self.i = (current_i + count) % len(self.items)
        return self

    def __isub__(self, count):
        current_i = self.i
        self.i = (current_i - count) % len(self.items)
        return self

    def __repr__(self):
        return str(self.items[self.i])

    def reset(self):
        self.i = 0

    def walk(self):
        self.__iadd__(1)

class NamedList(list):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __repr__(self):
        return ('{}: {}'.format(self.name, super().__repr__()))


if __name__ == '__main__':
    pass