from gntools.numbers import Nr, IntNr, InvalidNumberError
from gntools.numbers.roman import RomanNr, roman_nums

def number(n):
    if isinstance(n, str) and all(c in roman_nums for c in n):
        return RomanNr(n)
    try:
        return IntNr(n)
    except:
        pass
    try:
        return Nr(n)
    except:
        raise InvalidNumberError('Invalid number: {}'.format(n))


