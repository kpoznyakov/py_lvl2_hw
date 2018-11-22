def max_numbers(*args):
    return max(args)


def max_len_on_str(*args):
    return max(args, key=len)


def summary_str(name, age, city, first_login='NEWER', *args, **kwargs):
    return f'{name}, возраст: {age}, проживает в {city}. ' \
           f'Дополнительно: {list(map(str, args))}. \nStatus: {kwargs} \nFirst login: {first_login}'


def test_max_number():
    assert max_numbers(123, 45, 678) == 678
    assert max_numbers(-123, 12, 0) == 12


def test_max_len():
    assert max_len_on_str('Hello, world!', '15', '143', 'min') == 'Hello, world!'
    assert max_len_on_str('12', '\t') == '12'


def test_summary_str():
    assert summary_str('Username', '21', 'Vladivistok', '15.09.2018',
                       'Some', 'additional', 'parameters',
                       one='more') == "Username, возраст: 21, проживает в Vladivistok. " \
                                      "Дополнительно: ['Some', 'additional', 'parameters']. \n" \
                                      "Status: {'one': 'more'} \n" \
                                      "First login: 15.09.2018"
