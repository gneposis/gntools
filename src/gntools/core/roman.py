import re

class OutOfRangeError(ValueError): pass
class NotIntegerError(ValueError): pass
class InvalidRomanNumeralError(ValueError): pass

roman_nums = ('I', 'V', 'X', 'L', 'C', 'D', 'M')

roman_numeral_map = ( ('M', 1000),
                      ('CM', 900),
                      ('D',  500),
                      ('CD', 400),
                      ('C',  100),
                      ('XC',  90),
                      ('L',   50),
                      ('XL',  40),
                      ('X',   10),
                      ('IX',   9),
                      ('V',    5),
                      ('IV',   4),
                      ('I',    1) )

roman_numeral_pattern = re.compile('''
    ^                   # beginning of string
    M{0,3}              # thousands - 0 to 3 Ms
    (CM|CD|D?C{0,3})    # hundreds - 900 (CM), 400 (CD) 0-300 (0 to 3 Cs),
                        #     or 500-800 (D, followed 1 to 3 Cs)
    (XC|XL|L?X{0,3})    # tens - 90 (XC), 40 (XL), 0-30 (0 to 3 Xs),
                        #     or 50-80 (L, followed by 0 to 3 Xs)
    (IX|IV|V?I{0,3})    # ones - 9 (IX), 4 (IV), 0-3 (0 to 3 Is),
                        #     or 5-8 (V, followed by 0 to 3 Is)
    $                   # end of string
    ''', re.VERBOSE)

def is_roman(s):
    num_set = set(roman_nums)
    try:
        for c in s:
            if c.upper() not in num_set:
                return False
    except:
        return False
    return True

def to_roman(n):
    # Code is from Dive Into Python 3
    '''convert integer to Roman numeral'''

    if not isinstance(n, int):
        raise NotIntegerError('non-integers can not be converted')
    
    if not (0 < n < 4000):
        raise OutOfRangeError('number out of range (must be less than 4000)')
    
    result = ''
    for numeral, integer in roman_numeral_map:
        while n >= integer:
            result += numeral
            n -= integer
    return result


def from_roman(s):
    # Code is from Dive Into Python 3
    """convert Roman numeral to integer"""
    if not s:
        raise InvalidRomanNumeralError('Input can not be blank')
    if not roman_numeral_pattern.search(s):
        raise InvalidRomanNumeralError('Invalid Roman numeral: {0}'.format(s))

    result = 0
    index = 0
    for numeral, integer in roman_numeral_map:
        while s[index:index+len(numeral)] == numeral:
            result += integer
            index += len(numeral)
    return result

