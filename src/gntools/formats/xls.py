"""
Module for managing Excel (xls) file format.
Usage: File(xls_file)
"""

# xls.py by Adam Szieberth (2013)
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
import xlrd

import gntools.formats

class File(gntools.formats.File):
    def __init__(self, path):                             
        super().__init__(path)

        self.obj = xlrd.open_workbook(self.fullpath).sheet_by_index(0)

    def regular_norm(self):
        """Converts objects to pythonic ones."""
        result = list()
        for r in range(self.obj.nrows):
            row_data = list()
            for c in range(self.obj.ncols):
                row_data.append(norm_cell(self.obj.row(r)[c]))
            result.append(row_data)
        return result

    def trimmed_norm(self, from_end=True, keep_empty=True):
        """
        Like regular_norm, but trims None cells from end of rows (or from
        the beginning of rows if from_end=False). Keeps empty lines by
        default.
        """
        def trimmer(normed_obj):
            for row in normed_obj:
                if from_end:
                    i, adjust = -1, -1
                else:
                    i, adjust = 0, 1
                while True:
                    try:
                        cell = row[i]
                    except: # row is empty
                        if keep_empty:
                            yield []
                        break
                    else:
                        if cell is None:
                            i += adjust
                        else:
                            if i == 0 or i == -1:
                                yield row
                            elif i < 0:
                                yield row[:i+1]
                            else:
                                yield row[i:]
                            break

        normed_obj = self.regular_norm()
        return [row for row in trimmer(normed_obj)]

def norm_cell(cell_data):
    if cell_data.ctype == 0:
        return None
    elif cell_data.ctype == 1:
        return cell_data.value
    elif cell_data.ctype == 2:
        if int(cell_data.value) == cell_data.value:
            return int(cell_data.value)
        else:
            return float(cell_data.value)

if __name__ == '__main__':
    pass