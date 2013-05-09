class InvalidNumberError(ValueError): pass

class Nr:
    def __init__(self, number, comma={'.', ','}):
        if isinstance(number, str):
            number = floatize(number, comma=comma)

        if isinstance(number, str):
            self.value = int(number)
        elif isinstance(number, float):
            if number == int(number):
                self.value = int(number)
            else:
                self.value = number
        elif isinstance(number, int):
            self.value = number
        else:
            raise InvalidNumberError('Invalid number: {}'.format(number))

    def _get_val(self, num):
        try:
            return num.value
        except:
            return num        

    def __eq__(self, num):
        if self.value == self._get_val(num):
            return True
        return False
    def __ge__(self, num):
        if self.value >= self._get_val(num):
            return True
        return False
    def __gt__(self, num):
        if self.value > self._get_val(num):
            return True
        return False
    def __le__(self, num):
        if self.value <= self._get_val(num):
            return True
        return False
    def __lt__(self, num):
        if self.value < self._get_val(num):
            return True
        return False
    def __ne__(self, num):
        if self.value != self._get_val(num):
            return True
        return False

    def __hash__(self):
        return self.value.__hash__()

    def __repr__(self):
        return str(self.value)

class IntNr(Nr):
    def __init__(self, number):
        if isinstance(number, str):
            self.value = int(number)
        elif isinstance(number, float) and number == int(number):
            self.value = int(number)
        elif isinstance(number, int):
            self.value = number
        else:
            raise InvalidNumberError('Invalid number: {}'.format(number))

def floatize(s, comma={'.', ','}):
    for c in comma:
        if c in s:
            return float(s.replace(c, '.'))