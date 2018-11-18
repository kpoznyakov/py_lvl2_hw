from client import *
import datetime

if __name__ == '__main__':
    assert message('message') == {'action': 'msg',
                                  'time': get_current_time(),
                                  'user': {'account_name': username,
                                           'msg': 'message'}
                                  }, 'Not equal'
    assert get_current_time() == str(datetime.datetime.now().replace(microsecond=0).isoformat(sep=' ')), 'Time ERR'
    assert auth() == {
        'action': 'authenticate',
        'time': get_current_time(),
        'user': {'account_name': username,
                 'password': password}
    }, 'Auth error'
    assert presence() == {
        'action': 'presence',
        'time': get_current_time(),
        'type': 'status',
        'user': {
            'account_name': username,
            "status": "OK"
        }
    }, 'Presence error'
    assert message('somemessage') == {'action': 'msg',
                                      'time': get_current_time(),
                                      'user': {'account_name': username,
                                               'msg': 'somemessage'}
                                      }, 'Message error'
    assert encode_msg({'message': 'ok'}) == b'{"message": "ok"}'
    assert decode_msg(b'{"message": "ok"}') == {'message': 'ok'}
