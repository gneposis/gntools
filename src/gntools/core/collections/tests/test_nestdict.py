import copy

import pytest

import nestdict

class Test635483:
    """
    Test nestdict on Stack Overflow Question #635483:
        What is the best way to implement nested dictionaries in Python?
        http://stackoverflow.com/questions/635483
    """
    def setup_method(self, method):
        self.d = [(['new jersey', 'mercer county', 'plumbers'], 3),
                  (['new jersey', 'mercer county', 'programmers'], 81),
                  (['new jersey', 'middlesex county', 'programmers'], 81),
                  (['new jersey', 'middlesex county', 'salesmen'], 62),
                  (['new york', 'queens county', 'plumbers'], 9),
                  (['new york', 'queens county', 'salesmen'], 36)]

        self.expected = {'new jersey':
                            {'mercer county': {'plumbers': 3,
                                               'programmers': 81},
                             'middlesex county': {'programmers': 81,
                                                  'salesmen': 62}},
                         'new york': {
                             'queens county': {'plumbers': 9,
                                               'salesmen': 36}}}

    def get_parts(self):
        """
        Splits self.d into two separate NestedDicts.
        """
        part1 = nestdict.NestedDict()
        part2 = nestdict.NestedDict()
        for i in range(0, len(self.d), 2):
            part1[self.d[i][0]] = self.d[i][1]
        for i in range(1, len(self.d), 2):
            part2[self.d[i][0]] = self.d[i][1]
        return part1, part2

    def test_retype(self):
        """
        Test of retype function. Implicitly it also tests getitem
        function and NestedDict's __getitem__ function on lists.
        """
        retyped = nestdict.retype(self.expected, nestdict.NestedDict)
        for subdirpath in nestdict.paths(retyped, of_values=False):
            assert type(retyped[subdirpath]) == nestdict.NestedDict
        retyped2 = nestdict.retype(retyped, dict_type=dict)
        for subdirpath in nestdict.paths(retyped2, of_values=False):
            assert type(nestdict.getitem(retyped2, subdirpath)) == dict

    def test_NestedDict(self):
        """
        Test of NestedDict class.        
        """
        nesteddict = nestdict.NestedDict()
        for d in self.d:
            nesteddict[d[0]] = d[1]
        assert nesteddict == self.expected
        for subdirpath in nestdict.paths(nesteddict, of_values=False):
            assert type(nesteddict[subdirpath]) == nestdict.NestedDict
        return nesteddict

    def test_NestedDict_setitem__(self):
        """
        Test of NestedDict class' __setitem__ method. It also tests
        NestedDict's get_lock() method. 
        """
        nesteddict = self.test_NestedDict()
        pathbase = ['new jersey', 'mercer county']
        nesteddict[pathbase + ['plumbers', 'test']] = 1
        expected = {'plumbers': {'test': 1}, 'programmers': 81}
        assert nesteddict[pathbase] == expected
        # Now we lock the dictionary at pathbase. Each fake-extended
        # longer path should return the last valid lock state.
        assert nesteddict.get_lock(pathbase) == False
        assert nesteddict.get_lock(pathbase + ['fake']) == False
        nesteddict[pathbase].lock = True
        assert nesteddict.get_lock(pathbase + ['fake']) == True
        # So we try to change a locked value
        nesteddict[pathbase + ['programmers']] -= 1
        # No change should be done
        assert nesteddict[pathbase] == expected
        # Now we try to extend it...
        nesteddict[pathbase + ['programmers', 'test']] = 1
        # Still no change should be done
        assert nesteddict[pathbase] == expected
        # Although the lock of the main dictionary is still open
        assert nesteddict.lock == False

    def test_NestedDict_paths(self):
        """
        Test of NestedDict class' path method.        
        """
        nesteddict = self.test_NestedDict()
        paths = {tuple(p) for p in nesteddict.paths()}
        expected = {tuple(e[0]) for e in self.d}
        assert paths == expected
        expected_subdirs = {('new jersey',),
                            ('new jersey', 'mercer county'),
                            ('new jersey', 'middlesex county'),
                            ('new york',),
                            ('new york', 'queens county'),
                            }
        subdirs = {tuple(p) for p in nesteddict.paths(of_values=False)}
        assert subdirs == expected_subdirs

    def test_NestedDict_merge(self):
        """
        Test of NestedDict class' merge method.
        """
        part1, part2 = self.get_parts() 
        part1.merge(part2)
        assert part1 == self.expected
        part1, part2 = self.get_parts()
        # Now we lock a path and merge the two dictionaries
        part1[['new jersey', 'mercer county']].lock = True
        part1.merge(part2)
        expected = copy.deepcopy(self.expected)
        del expected['new jersey']['mercer county']['programmers']
        # programmers should not merged to the locked path
        assert part1 == expected
        # And no overwrite should be done on that locked path
        part2[['new jersey', 'mercer county', 'plumbers']] = 10
        part1.merge(part2)
        assert part1 == expected
        # Now we unlock that path
        part1[['new jersey', 'mercer county']].lock = False
        part1.merge(part2)
        expected = copy.deepcopy(self.expected)
        expected['new jersey']['mercer county']['plumbers'] = 10
        assert part1 == expected

    def test_close_open_lock(self):
        """
        Test of NestedDict class' lock and unlock methods.
        """
        nesteddict = self.test_NestedDict()
        nesteddict.lock_close()
        for p in nestdict.paths(nesteddict, of_values=False):
            assert nesteddict[p].lock == True
        assert nesteddict[p].__setitem__(['test'], 1) == False
        nesteddict['new jersey'].lock_open()
        assert nesteddict['new jersey'].__setitem__(['test'], 1) == True
        assert nesteddict['new york'].__setitem__(['test'], 1) == False
        expected = copy.deepcopy(self.expected)
        expected['new jersey']['test'] = 1
        assert nesteddict == expected

    def test_main(self):
        """
        Test of main() function.
        """
        assert nestdict.main() == self.expected

class Test9730648:
    """
    Test nestdict on Stack Overflow Question #9730648:
        Merge a nested dictionary (default values)
        http://stackoverflow.com/questions/9730648/
    """
    def setup_method(self, method):
        self.defaults = {
           'svn': "",
           'notify': {
              'email': "",
              'notifo': { 'username': "", 'secret': ""},
              'active': False,
              'lastCheck': 0
           }
        }

        self.defaults_paths_v = [['svn'],
                                 ['notify', 'email'],
                                 ['notify', 'notifo', 'username'],
                                 ['notify', 'notifo', 'secret'],
                                 ['notify', 'active'],
                                 ['notify', 'lastCheck'],]
        self.defaults_paths_d = [['notify'], ['notify', 'notifo']]
        self.defaults_vals = ["", "", "", "", False, 0,]

        self.local =  {
           'svn': "/path/to/trunk/",
           'notify': {
              'email': "me@mysite.com",
              'notifo': { 'username': "me", 'secret': "1234"},
           }
        }

        self.local_paths = [['svn'],
                            ['notify', 'email'],
                            ['notify', 'notifo', 'username'],
                            ['notify', 'notifo', 'secret'],]
        self.local_vals = ["/path/to/trunk/",
                           "me@mysite.com", "me", "1234",]

        self.local_expected =  {
           'svn': "/path/to/trunk/",
           'notify': {
              'email': "me@mysite.com",
              'notifo': { 'username': "me", 'secret': "1234"},
              'active': False,
              'lastCheck': 0
           }
        }
        self.local_expected_vals = ["/path/to/trunk/",
                                    "me@mysite.com",
                                    "me",
                                    "1234",
                                    False,
                                    0,]

        self.checklist = [
                          (self.defaults,
                           self.defaults_paths_v,
                           self.defaults_vals),

                          (self.local,
                           self.local_paths,
                           self.local_vals),

                          (self.local_expected,
                           self.defaults_paths_v,
                           self.local_expected_vals),
                          ]

    def test_paths(self):
        """
        Test of nestdict.paths generator function.
        """
        for e in self.checklist:
            print('Expected value paths:\n{}'.format(sorted(e[1])))
            calculated = sorted([p for p in nestdict.paths(e[0])])
            print('Calculated value paths:\n{}'.format(calculated))
            assert sorted(e[1]) == calculated
            print('Expected subdir paths:\n{}'
                  .format(sorted(self.defaults_paths_d)))
            calculated = sorted([p for p in
                                 nestdict.paths(e[0], of_values=False)])
            print('Calculated subdir paths:\n{}'.format(calculated))
            assert sorted(self.defaults_paths_d) == calculated

    def test_invalid_paths(self):
        """
        Test if nestdict.get and nestdict.set raises exception for nonlist
        or nonempty paths.
        """
        bad_attr = ['svn', True, 0, None, (1, 2, 3),]
        for a in bad_attr:
            with pytest.raises(TypeError):
                nestdict.getitem(self.local_expected, a)
            with pytest.raises(TypeError):
                nestdict.setitem(self.local_expected, a, True)
        with pytest.raises(Exception):
            nestdict.getitem(self.local_expected, [])
        with pytest.raises(Exception):
            nestdict.setitem(self.local_expected, [], True)

    def test_getitem(self):
        """
        Test of nestdict.get function.
        """
        for e in self.checklist:
            for i, path in enumerate(e[1]):
                print('Dictionary path:\n{}'.format(path))
                print('Expected value:\n{}'.format(e[2][i]))
                calculated = nestdict.getitem(e[0], path)
                print('Calculated value:\n{}'.format(calculated))
                assert e[2][i] == calculated

    def test_setitem(self):
        """
        Test of nestdict.setitem function.
        """
        d = dict()
        for i, path in enumerate(self.defaults_paths_v):
            assert nestdict.setitem(d, path, self.local_expected_vals[i]
                                 ) == True
        assert self.local_expected == d
        assert nestdict.setitem(d,
                             self.defaults_paths_v[1],
                             self.local_expected_vals[1],
                             ) == None
        assert nestdict.setitem(d,
                             self.defaults_paths_v[1],
                             "me@mysite.org",
                             overwrite = False,
                             ) == False
        assert nestdict.getitem(d, self.defaults_paths_v[1]
                             ) == self.local_expected_vals[1]
        assert nestdict.setitem(d,
                             self.defaults_paths_v[1],
                             "me@mysite.org",
                             ) == True
        assert nestdict.getitem(d, self.defaults_paths_v[1]
                             ) == "me@mysite.org"
        assert nestdict.setitem(d,
                             ['notify', 'email', 'at'],
                             "mysite.com",
                             restruct = False,
                             ) == False
        assert nestdict.setitem(d,
                             ['notify', 'email', 'at'],
                             "mysite.com",
                             ) == True
        assert nestdict.getitem(d, ['notify', 'email']
                             ) == {'at': "mysite.com"}
        # Without overwrite permission, no restructing should be done
        assert nestdict.setitem(d,
                             ['notify', 'email', 'at', 'base'],
                             "mysite",
                             overwrite = False,
                             ) == False

    def test_merge(self):
        """
        Test of nestdict.merge function.
        """
        assert nestdict.merge(self.defaults, self.local,
                              return_new = True,
                              ) == self.local_expected
        assert self.defaults['svn'] == ''
        local = copy.deepcopy(self.local)
        assert nestdict.merge(local, self.defaults,
                              func_if_overwrite = False,
                              ) == self.local_expected
        assert local == self.local_expected

        def ow_func(path, dictobj1, dictobj2):
            """
            Just a test func_if_overwrite which allows overwrite only if
            last part of a path is 'email'.
            """
            if path[-1] == 'email':
                return True
            return False

        def ex_func(path, dictobj1, dictobj2):
            """
            Just a test func_if_exted which allows extension only if
            last part of a path is 'email'.
            """
            if path[-1] == 'lastCheck':
                return True
            return False

        d = nestdict.merge(self.defaults, self.local,
                           func_if_overwrite = ow_func,
                           return_new = True)
        assert d['svn'] == ''
        assert d['notify']['email'] == "me@mysite.com"
        d = nestdict.merge(self.local, self.defaults,
                           func_if_extend = ex_func,
                           func_if_overwrite = False,      
                           return_new = True)
        with pytest.raises(KeyError):
            d['notify']['active']
        assert d['notify']['lastCheck'] == 0

class Test12586179:
    """
    Test nestdict on Stack Overflow Question #12586179:
        Convert list of dictionaries to nested dictionary
        http://stackoverflow.com/questions/12586179
    """
    def setup_method(self, method):
        self.d = [{'name': 'Jim', 'attribute': 'Height', 'value': 6.3},
                  {'name': 'Jim', 'attribute': 'Weight', 'value': 170},
                  {'name': 'Mary', 'attribute': 'Height', 'value': 5.5},
                  {'name': 'Mary', 'attribute': 'Weight', 'value': 140}, ]
        self.expected = {'Jim': {'Height' : 6.3, 'Weight' : 170 },
                         'Mary': {'Height' : 5.5, 'Weight' : 140 },}

    def test_nestdict_NestedDict(self):
        """
        Test of NestedDict class.
        """
        result = nestdict.NestedDict()
        for d in self.d:
            result[[d['name'], d['attribute']]] = d['value']
        assert result == self.expected
