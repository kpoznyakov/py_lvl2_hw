from client import *


def test_presence():
    assert presence('some name') == {
        'action': 'presence',
        'time': get_current_time(),
        'type': 'status',
        'user': {
            'account_name': 'some name',
            "status": "OK"
        }
    }


def test_auth():
    assert auth('some name', 'some pass') == {
        'action': 'authenticate',
        'time': get_current_time(),
        'user': {'account_name': 'some name',
                 'password': 'some pass'}
    }


def test_decode():
    assert decode_msg(b'{"message": "message text"}') == {"message": "message text"}


def test_encode():
    assert encode_msg({"message": "message text"}) == b'{"message": "message text"}'
