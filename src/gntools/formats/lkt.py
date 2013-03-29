"""
Module for managing gntools .lkt (lookup table) file format.
Usage: File(lkt_file)

    LKT file format:
      - First line is for header titles separated by spaces.

      - Second line contains the type of the column data (float, int,
        str). Empty string there indicates default type identification.
        That means we try to convert the corresponding string to integer
        or float, and if that fails, we leave it as string.

      - Third line is for the rule which defines the maximum length of
        the records below.

      - After this, data.
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

from gntools.core.collections import DictList
from gntools.core.types import deftype


def validation(obj, header=None):
    """Does input object validation and returns number of columns."""
    class IncompatibleParentClassError(Exception): pass
    class VariableItemCountError(Exception): pass

    columns = None

    for i in obj:
        if not isinstance(i, list) and not isinstance(i, tuple):
            raise IncompatibleParentClassError(
                'Class of item is not list or tuple: {}'
                .format(i.__class__.__name__))
        if columns is None:
            columns = len(i)
        elif columns != len(i):
            raise VariableItemCountError(
                'Current item length ({}) differs from previous ({}).'
                .format(len(i), columns))
    
    if header and not isinstance(header, list) and (
                                           not isinstance(header, tuple)):
        raise IncompatibleParentClassError(
            'Class of header is not list or tuple: {}'
            .format(header.__class__.__name__))
    elif header and len(header) != columns:
            raise VariableItemCountError(
                'Length of header ({}) differs from item length ({}).'
                .format(len(header), columns))        

    return columns

def check_indent(columns, indent=None):
    """Returns indent string or checks an indent string if it is valid."""
    VALID_INDENTS = 'lcr' 
    class InvalidJustificationDeclarationError(Exception): pass

    if indent and not isinstance(indent, str):
        raise IncompatibleParentClassError(
            'Class of indent is not string: {}'
            .format(indent.__class__.__name__))
    elif indent and len(indent) != columns:
            raise VariableItemCountError(
                'Length of indent ({}) differs from item length ({}).'
                .format(len(indent), columns))
    elif indent:
            for i in indent:
                if i not in VALID_INDENTS:
                    raise InvalidJustificationDeclarationError(
                    'Justification declaration {} is not valid in {}.'
                    .format(i, VALID_INDENTS))
    else:
        indent = VALID_INDENTS[0]*columns

    return indent

def get_col_widths(obj, columns=None, header=None, class_names=None):
    """Returns the lengths of columns."""
    if columns is None:
        columns = validation(obj, header=header)
    max_lengths = [None for i in range(columns)]
    for i in obj:
        for e in enumerate(i):
            max_length = max_lengths[e[0]]
            if max_length is None:
                max_lengths[e[0]] = len(str(e[1]))
            else:
                max_lengths[e[0]] = max(max_length, len(str(e[1])))

    if header:
        for e in enumerate(header):
            max_length = max_lengths[e[0]]
            max_lengths[e[0]] = max(max_length, len(str(e[1])))

    if class_names:
        for e in enumerate(class_names):
            max_length = max_lengths[e[0]]
            max_lengths[e[0]] = max(max_length, len(str(e[1])))

    return max_lengths

def get_col_classes(obj, columns=None, strict=True):
    """
    Returns the class names of data in the columns. If strict, class names
    must be identical.
    """
    class ClassNotIdenticalError(Exception): pass

    numcls = {'int', 'float'}

    if columns is None:
        columns = validation(obj)
    class_names = [None for i in range(columns)]
    for i in obj:
        for e in enumerate(i):
            class_name = class_names[e[0]]
            if class_name is None:
                class_names[e[0]] = e[1].__class__.__name__
            elif class_name != e[1].__class__.__name__ and strict:
                raise ClassNotIdenticalError(
                    'Class ({}) differs from the one expected ({}).'
                    .format(e[1].__class__.__name__, class_name))
            elif not strict and class_name != e[1].__class__.__name__:
                if (class_name in numcls) and (
                                       e[1].__class__.__name__ in numcls):
                    class_names[e[0]] = 'float'
                class_names[e[0]] = 'str'
    return class_names

def add_row(rowobj, widths=None, indent=None, space=1):

    format_string_normal = '{}' + ' '*space
    format_string_last = '{}\n'

    result = ''
    for e in enumerate(rowobj):
        if e[0] < len(rowobj) - 1:
            format_string = format_string_normal
        else:
            format_string = format_string_last

        try:
            ind = indent[e[0]]
        except:
            ind = 'l'
        try:
            width = widths[e[0]]
        except:
            width = len(str(e[1]))

#        print(ind,width)
        if ind == 'c':
            result += format_string.format(str(e[1]).center(width))
        else:
            result += format_string.format(getattr(str(e[1]),
                                             '{}just'.format(ind))(width))
    return result

class FromObj:

    def __init__(self, obj, header=None, strict=True):
        self.obj = obj
        self.strict = strict

        if header is None:
            try:
                self.header = self.obj.header
            except:
                self.header = header
        else:
            self.header = header

        self.columns = validation(self.obj, header=self.header)
        self.col_classes = get_col_classes(self.obj,
                                           columns=self.columns,
                                           strict=self.strict)
        self.col_widths = get_col_widths(self.obj,
                                         columns=self.columns,
                                         header=self.header,
                                         class_names=self.col_classes)

    def __call__(self, indent=None, space=1):
        ind = check_indent(self.columns, indent)
        result = ''
        if self.header:
            result += add_row(self.header, self.col_widths, ind, space)
        result += add_row(self.col_classes, self.col_widths, ind, space)
        result += add_row(['-'*w for w in self.col_widths], space=space)
        for i in self.obj:
            result += add_row(i, self.col_widths, ind, space)
        return result.rstrip('\n')








#def import_(object, header=None, indent=None, strict=True, space=1):
#    """
#    Imports an object to lkt if possible.
#
#      - indent should be a string of the following chars: l, c, r. These
#        three represents left, center and right justification. For example
#        for a three column LKT the following indent is valid: indent = 'rll' 
#
#    Compatible classes:
#      - gntools.collections.ListList
#    """
#
#    format_string_normal = '{}' + ' '*space
#    format_string_last = '{}\n'
#
#    # Initial validation - - - - - - - - - - - - - - - - - - - - - - - - -
#    itemcount = None
#    for i in object:
#        if not isinstance(i, list) and not isinstance(i, tuple):
#            raise IncompatibleParentClassError(
#                'Class of item is not list or tuple: {}'
#                .format(i.__class__.__name__))
#        if itemcount is None:
#            itemcount = len(i)
#        elif itemcount != len(i):
#            raise VariableItemCountError(
#                'Current item length ({}) differs from previous ({}).'
#                .format(len(i), itemcount))
#
#    if header and not isinstance(header, list) and (
#                                           not isinstance(header, tuple)):
#        raise IncompatibleParentClassError(
#            'Class of header is not list or tuple: {}'
#            .format(header.__class__.__name__))
#    elif header and len(header) != itemcount:
#            raise VariableItemCountError(
#                'Length of header ({}) differs from item length ({}).'
#                .format(len(header), itemcount))        
#
#    if indent and not isinstance(indent, str):
#        raise IncompatibleParentClassError(
#            'Class of indent is not string: {}'
#            .format(indent.__class__.__name__))
#    elif indent and len(indent) != itemcount:
#            raise VariableItemCountError(
#                'Length of indent ({}) differs from item length ({}).'
#                .format(len(indent), itemcount))
#    elif indent:
#            for i in indent:
#                if i not in VALID_JUSTS:
#                    raise InvalidJustificationDeclarationError(
#                    'Justification declaration {} is not valid in {}.'
#                    .format(i, VALID_JUSTS))
#    else:
#        indent = 'l'*itemcount
#    # End of initial validation  - - - - - - - - - - - - - - - - - - - - -
#
#    max_lengths = [None for i in range(itemcount)]
#    class_names = [None for i in range(itemcount)]
#
#    for i in object:
#        for e in enumerate(i):
#
#            j = e[0]
#            item = e[1]
#            max_length = max_lengths[j]
#            class_name = class_names[j]
#
#            if max_length is None:
#                max_lengths[j] = len(str(item))
#            else:
#                max_lengths[j] = max(max_length, len(str(item)))
#
#            if class_name is None:
#                class_names[j] = item.__class__.__name__
#            elif class_name != item.__class__.__name__ and strict:
#                raise ClassNotIdenticalError(
#                    'Class ({}) differs from the one expected ({}).'
#                    .format(item.__class__.__name__, class_name))
#            elif class_name != item.__class__.__name__ and not strict:
#                class_names[j] = 'str'
#
#    if header:
#        for e in enumerate(header):
#            max_length = max_lengths[e[0]]
#            max_lengths[e[0]] = max(max_length, len(str(e[1])))
#
#    for e in enumerate(class_names):
#        max_length = max_lengths[e[0]]
#        max_lengths[e[0]] = max(max_length, len(str(e[1])))
#
#    # Function to add rows to result - - - - - - - - - - - - - - - - - - - 
#    def add_row(source):
#        result = ''
#        for e in enumerate(source):
#
#            if e[0] < len(source) - 1:
#                format_string = format_string_normal
#            else:
#                format_string = format_string_last
#
#            if indent[e[0]] == 'c':
#                result += format_string.format(str(e[1])
#                                               .center(max_lengths[e[0]]))
#            else:
#                indentstr = '{}just'.format(indent[e[0]])
#                result += format_string.format(
#                                               getattr(
#                                                       str(e[1]),
#                                                       indentstr
#                                                       )
#                                                       (max_lengths[e[0]])
#                                               )
#        return result
#    # End of function  - - - - - - - - - - - - - - - - - - - - - - - - - -
#
#    result = ''
#
#    if header:
#            result += add_row(header)
#
#    result += add_row(class_names)
#
#    for i in max_lengths[:-1]:
#        result += format_string_normal.format('-'*i)
#    result += format_string_last.format('-'*max_lengths[-1])
#
#    for i in object:
#        result += add_row(i)
#
#    return result.rstrip('\n')












if __name__ == '__main__':
    pass