"""
Module for file and directory management.
Usage:
"""

# observer.py by Adam Szieberth (2013)
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
__all__ = ['wotdossiercache']

import datetime
import os
import threading
import time

# TODO: Links
# TODO: plain text fingerprints / sxntax highlighting / comparing
# Note: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/

from gntools.formats.readers.hashcalc import md5f as md5sum
import gntools.formats

CHECK_FREQUENCY=25
LOG_STRING = '{} -- {}: **{}**>>**{}**' # time, name, args, result

verbatim = False

def logger(func):
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        if not (len(args) == 1 and args[0] == result
                                                ) and verbatim and result:
            with StdIn().lock:
                print(LOG_STRING.format(
                                        datetime.datetime.now(),
                                        func.__name__,
                                        args,
                                        result
                                        ))
        return result
    return inner

@logger
def addr(path):
    return os.path.abspath(path).replace('\\', '/')

@logger
def dirname(path):
    return os.path.dirname(path)

@logger
def name(path):
    return os.path.basename(path)

@logger
def ls(path, verbose=False):
    result = {'d': [], 'f': []}
    fullpath = addr(path)
    if verbose > 1: print('* ls startfullpath: {}'.format(fullpath))
    elemlist = [e for e in os.listdir(fullpath)]
    if verbose > 1: print('* ls elemlist: {}'.format(elemlist))
    for elem in elemlist:
        elemfullpath = addr('{}/{}'.format(fullpath, elem))
        if verbose > 1:
            print('* ls elemfullpath: {}'.format(elemfullpath))
        if os.path.isdir(elemfullpath):
            result['d'].append(elemfullpath)
        elif os.path.isfile(elemfullpath):
            result['f'].append(elemfullpath)
    return result

class StdIn:
    lock = threading.Lock()
        

class Path:
    def __init__(self, path, hashing=False):
        self.fullpath = addr(path)
        self.hashing = hashing
        self.changes = set()
        self.lock = threading.Lock()

    def __repr__(self):
        return self.fullpath

    def investigate(self, frequency=CHECK_FREQUENCY):
        self.detective = Detective(self, frequency=frequency)
        self.detective.start()


class File(Path):
    def __init__(self, path, hashing=False):
        super().__init__(path, hashing=hashing)
        self.previous_report = self._report()
        self.report = self.previous_report


    def bnametup(self):
        """Returns the splitted basename."""
        return os.path.splitext(os.path.basename(self.fullpath))

    @logger
    def size(self):
        return os.stat(self.fullpath).st_size

    # /------------------------------------------------------------------\
    # the following keys were named based on this documentation:
    # http://www.tutorialspoint.com/python/os_stat.htm
    # If tutorialspoint disagree with my licensing, please contact me!

    # TODO: date modes with decorators

    @logger
    def lastaccess(self):
        return datetime.datetime.fromtimestamp(
                              os.stat(self.fullpath).st_atime).isoformat()
    @logger
    def lastmetachange(self):
        return datetime.datetime.fromtimestamp(
                              os.stat(self.fullpath).st_mtime).isoformat()
    @logger
    def lastcontentchange(self):
        return datetime.datetime.fromtimestamp(
                              os.stat(self.fullpath).st_ctime).isoformat()

    # \------------------------------------------------------------------/

    @logger
    def md5sum(self):
        return md5sum(self.fullpath)

    @logger
    def _report(self):
        result = {
                  'name': name(self.fullpath),
                  'path': dirname(self.fullpath),
                  'size': self.size(),
                  'lastaccess': self.lastaccess(),
                  'lastmetachange': self.lastmetachange(),
                  'lastcontentchange': self.lastcontentchange(),
                  'hashing': self.hashing,
                  }
        if self.hashing:
            result.update({'md5sum': self.md5sum()})

        return result

    @logger
    def changed(self):
        self.changes = set()

        if not os.path.exists(self.fullpath):
            self.changes.add('deleted')
            return self.changes

        if self.size() != self.report['size']:
            self.changes.add('size')
        if self.lastaccess() != self.report['lastaccess']:
            self.changes.add('lastaccess')
        if self.lastmetachange() != self.report['lastmetachange']:
            self.changes.add('lastmetachange')
        if self.lastcontentchange() != self.report['lastcontentchange']:
            self.changes.add('lastcontentchange')

        if not self.hashing:
            return self.changes

        if self.md5sum() != self.report['md5sum']:
            self.changes.add('md5sum')

        if self.changes:
            self.previous_report = self.report
            self.report = self._report()
        return self.changes


class Directory(Path):
    def __init__(self, path, hashing=False):
        super().__init__(path, hashing=hashing)
        self.sub = set()
        self.files = set()
        dir_ = ls(self.fullpath)
        for fullpath in dir_['d']:
            self.sub.add(Directory(fullpath, hashing=self.hashing))
        for fullpath in dir_['f']:
            self.files.add(File(fullpath, hashing=self.hashing))

    @logger
    def changed(self, recursively=False):
        self.changes = set()
        # TODO: code recursiely=True case
        if not recursively:
            for f in self.files:
                changes = f.changed()
                if changes:
                    self.changes.add(f)
        return self.changes


class Detective(threading.Thread):
    def __init__(self,
                 PathObj,
                 frequency=CHECK_FREQUENCY,
                 ):
        self.target_ = PathObj
        self.frequency = frequency
        # Note: super().__init__(self) -->
        # AssertionError: group argument must be None for now
        threading.Thread.__init__(self)

    def run(self):
        while True:
            with self.target_.lock:
                self.changed = self.target_.changed()
            time.sleep(self.frequency)
