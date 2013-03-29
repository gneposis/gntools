"""
Module for converting data from World of Tanks related JSON files to best
fitting gneposis formats.

JSON files provided along by Marius (Phalynx) Czyz's
WoT-Dossier-Cache-to-JSON utility:
https://github.com/Phalynx/WoT-Dossier-Cache-to-JSON
"""

# phalynxjson.py by Adam Szieberth (2013)
# Python 3.3 (Windows)

# Full license text:
# ----------------------------------------------------------------------------
#                 DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                           Version 2, December 2004
#
# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>
#
# Everyone is permitted to copy and distribute verbatim or modified  copies of
# this license document, and changing it is allowed as long as the name is
# changed.
#
#                 DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#       TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
# 0. You just DO WHAT THE FUCK YOU WANT TO.
# ----------------------------------------------------------------------------
import glob
import json

from gntools.core.collections import DictList
from gntools.core.path import mloc

from gntools.formats import lkt
from gntools.formats import lst

DEFAULT_DOSSIERTYPE = 2
DEFAULT_TYPEID = 1

LIST_LOCATION = 'data/lists'
COUNTRY = 'countryid.lst'
TYPE = 'tanktype.lst'

JSON_LOCATION = 'data/json'
MAPS_GLOB = 'maps.json'
STRUCTURES_GLOB = 'structures_*.json'
TANKS = 'tanks.json'

LKT_LOCATION = 'data/tables'
TANKS_LKT = 'tanks.lkt'
TANK_TABLE_COLS = (
                   'key',
                   'icon',
                   'shorttitle',
                   'title',
                   'country',
                   'tanktype',
                   'tier',
                   )
TANK_TABLE_INDENT = 'rllllcr'


country = lst.File(mloc(__file__, '{}/{}'.format(LIST_LOCATION, COUNTRY)))
tanktype = lst.File(mloc(__file__, '{}/{}'.format(LIST_LOCATION, TYPE)))


def filter_uppercased(string):
    """Returns str of uppercased alphabets from string."""
    result = ''
    for ch in string:
        if ch.isalpha() and ch == ch.upper():
            result += ch
    return result


class Tank(dict):
    """Dictionary of tank data."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def key(self, typeid=DEFAULT_TYPEID):
        """Returns key used in dossier cache."""
        return (self['tankid'] << 8) + (self['countryid'] << 4) + typeid

    def dossier_key(self, dossiertype=DEFAULT_DOSSIERTYPE,
                                                   typeid=DEFAULT_TYPEID):
        """Returns dossier cache key."""
        return dossiertype, self.key(typeid=typeid)

    def country(self):
        """Returns name of the country."""
        return country[self['countryid']]

    def tanktype(self, longname=False):
        """
        Returns abbreviated type of tank.
        If keyword arg longname=True then it returns the full type string.
        """
        elem = tanktype[self['type']]
        if longname:
            return elem
        return filter_uppercased(elem)

    def shorttitle(self):
        """Returns the short title of a tank."""
        try:
            return self['title_short']
        except:
            return self['title']


class Tanks(DictList):
    """List of Tanks."""
    def __init__(self, itemclass=Tank):
        jsonloc = mloc(__file__, '{}/{}'.format(JSON_LOCATION, TANKS))
        with open(jsonloc) as json_f:
            jsonstring = json_f.read()
        jsondictlist = json.loads(jsonstring)
        
        result = []
        for e in jsondictlist:
            result.append(itemclass(e))
        super().__init__(result, itemclass=itemclass)

def export_tanks(writeout=False):
    report = Tanks().report(TANK_TABLE_COLS)
    result = lkt.FromObj(report)(indent=TANK_TABLE_INDENT)
    if writeout:
        with open(mloc(__file__, '{}/{}'.format(LKT_LOCATION, TANKS_LKT)),
                  mode='w') as tanks_lkt:
            tanks_lkt.write(result)
    return result

if __name__ == '__main__':
    pass