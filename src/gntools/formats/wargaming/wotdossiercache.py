"""
Module for World of Tanks dossier cache file format.
Usage: File(dossier_cache_file)
"""

# wotdossiercache.py by Adam Szieberth (2013)
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
import base64
from datetime import datetime
import os
import pickle
import struct

from gntools.core.iterable import split_by_lenlist
from gntools.core.path import mloc

import gntools.formats
import gntools.formats.dic as dic
import gntools.formats.lkt as lkt
import gntools.formats.sdf as sdf

from gntools.formats.wargaming.phalynxjson import LKT_LOCATION, TANKS_LKT

ENCODING = 'latin_1'
# valid encodings: cp1256, latin_1, iso8859_9

VERSION_STRUCT = '=h'

tanks_data = dict()
for tank in lkt.File(mloc(__file__, LKT_LOCATION, TANKS_LKT)).obj:
    key = tank['key']
    del tank['key']
    tanks_data[key] = tank

SDF_DIR = 'data/structs'
# Note: SDF_DIR must contain sdf files named as version integers,
#       e.g. 26.sdf

STRFORMAT = '='
STRNUMFRAGS = 'h'
STRFRAGS = 'h'
STRTANKS = 'l'

def get_structs(sdf_dir=SDF_DIR):
    """
    Returns dictionary where keys are version integers and values are the
    corresponding structure definitions.
    """
    abs_sdf_dir = mloc(__file__, sdf_dir)
    keys = [int(f.rstrip('.sdf')) for f in os.listdir(abs_sdf_dir)]
    values = [sdf.File('{}/{}.sdf'.format(abs_sdf_dir, v)) for v in keys]
    return dict(zip(keys, values))

class File(gntools.formats.File):
    class StructureDataDontMatchError(Exception): pass

    def __init__(self, path):
        super().__init__(path)
        self.version = None

        try:
            self.login, self.nick = _base32name(self.bnametup()[0])
        except:
            self.login, self.nick = 'n/a', 'n/a'

        self.rawobj = self.read()

        self.version = self.rawobj[0]

        keys = list()
        values = list()
        structs = get_structs()

        for key in self.rawobj[1]:

            # calling this many times is slow but we dont care yet
            keys.append(tankfromwgkey(key))

            rawval = self.rawobj[1][key]
            rawvaldata = rawval[1].encode(ENCODING)

            version = struct.unpack(VERSION_STRUCT,
                          rawvaldata[:struct.calcsize(VERSION_STRUCT)])[0]

            tank_sdf = structs[version]
            tank_data = tank_sdf.get_dict(rawvaldata, force_length=False)

            fragspos = tank_data['fragspos']
            del tank_data['fragspos']

            values.append((
                           datetime.fromtimestamp(rawval[0]),
                           TankData(tank_data),
                           get_frags(rawvaldata[fragspos:]),
                           ))

        self.obj = Tanks(zip(keys, values))

    def read(self):
        with open(self.fullpath, mode='rb') as f:
            r = pickle.load(f, encoding=ENCODING)
        return r

def get_frags(data):
    count_format = STRFORMAT + STRNUMFRAGS
    count_len = struct.calcsize(count_format)

    count = struct.unpack(count_format, data[:count_len])[0]

    fragged_tanks_format = STRFORMAT + STRTANKS*count
    frags_count_format = STRFORMAT + STRFRAGS*count

    tanks_data_len = struct.calcsize(fragged_tanks_format)
    frags_data_len = struct.calcsize(frags_count_format)

    lengths = [count_len, tanks_data_len, frags_data_len]
    sliced_data = [d for d in split_by_lenlist(data, lengths)]

    tuple_tanks = struct.unpack(fragged_tanks_format, sliced_data[1])
    tuple_frags = struct.unpack(frags_count_format, sliced_data[2])

    return Tanks(zip(tuple_tanks, tuple_frags))


def tankfromwgkey(wargaming_key):
    # The docstring informations are based on Marius (Phalynx) Czyz's
    # research: http://wiki.vbaddict.net/pages/File_Dossier
    # Marius, if you disagree with my licensing, please contact me!
    """
    Returns tank name from Wargaming.net key.

    The Wargaming.net key is a two length tuple:
      - The first item is the dossier_type integer. Values listed by index
            in data/lists/dossiertype.lst.
      - The second item is the type_comp_descr integer. It contains
        informations about the countryID and tankID of a tank.
            tankID = type_comp_descr >> 8 & 65535
            countryID = type_comp_descr >> 4 & 15
                Values listed by index in data/lists/countryid.lst.
            typeID = type_comp_descr & 15
                Values listed by index in data/lists/typeid.lst.
      - We, however, do not want to get trough this mess. So instead of
        that we use data/dicts/tanks.dic which contains type_comp_descr-s
        as keys and tank names as values.
    """
    return wargaming_key[1]

def _base32name(pure_file_name):
    """
    Returns (server, nickname) if pure filename (filename without
    extension) is a valid base32name.
    """
    try:
        base32name = base64.b32decode(pure_file_name)
    except:
        base32name = None
    else:
        base32name = base32name.decode(ENCODING)

    if base32name:
        return base32name.split(';')


class Tanks(dict):

    def get_by_tit(self, string, short=False, strict=True):
        result = list()
        for tank in self:
            if short:
                tit = tanks_data[tank]['shorttitle']
            else:
                tit = tanks_data[tank]['title']

            if strict and string.lower() == tit.lower():
                return self[tank]
            elif not strict and string.lower() in tit.lower():
                result.append((tit, self[tank]))

        return result

class TankData(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def damage_ratio(self):
        dealt = self['tankdata']['damageDealt']
        received = self['tankdata']['damageReceived']
        result = tankstats.damage_ratio(dealt, received)
        if isinstance(result, float):
            return '{:.2f}'.format(result)
        else:
            return result

if __name__ == '__main__':
    pass