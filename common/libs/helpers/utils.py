import random
import string


def get_string(length=8, char='lower'):
    chars = {'lower': string.ascii_lowercase,
             'upper': string.ascii_uppercase,
             'digits': string.digits,
             'mix': string.ascii_letters + string.digits}
    string_ = chars[char] if char in chars.keys() else string.ascii_letters
    return ''.join(random.choice(string_) for _ in range(length))
