from socket import *
import json
import argparse
import datetime
import time
import requests
from threading import Thread
from log.client_log_config import *


def random_name_generator():
    try:
        name = requests.post('https://api.codetunnel.net/random-nick', data='{"theme": "halloween"}').json()['nickname']
        return name
    except KeyError:
        return 'username_' + get_current_time()


parser = argparse.ArgumentParser()
parser.add_argument('-a', '--addr', type=str, help="IP to connect", default='localhost')
parser.add_argument('--port', type=int, help="port to connect", default=7777)
parser.add_argument('-u', '--user', type=str, help="username",
                    default=random_name_generator())
parser.add_argument('-p', '--password', type=str, help="password")
parser.add_argument('--debug', type=bool, help='debug flag', default=False)

args = parser.parse_args()

username = args.user
password = args.password

debug = args.debug


def decor_log_debug(func):
    if debug:
        def wrapper(*args, **kwargs):
            log.debug('Func "%s" got "%s", "%s"', func.__name__, args, kwargs)
            r = func(*args, **kwargs)
            return r

        return wrapper
    else:
        return func


def log_info():
    pass


@decor_log_debug
def get_current_time():
    return str(datetime.datetime.now().replace(microsecond=0).isoformat(sep=' '))


@decor_log_debug
def decode_msg(data_b):  # TODO вынести в файл общего кода
    return json.loads(data_b, encoding='utf-8')


@decor_log_debug
def encode_msg(data):  # TODO вынести в файл общего кода
    try:
        return json.dumps(data).encode('utf-8')
    except Exception:
        pass


@decor_log_debug
def auth(username, password):
    auth_msg = {
        'action': 'authenticate',
        'time': get_current_time(),
        'user': {'account_name': username,
                 'password': password}
    }
    return auth_msg


@decor_log_debug
def presence(name):
    presence_msg = {
        'action': 'presence',
        'time': get_current_time(),
        'type': 'status',
        'user': {
            'account_name': name,
            "status": "OK"
        }
    }
    return presence_msg


@decor_log_debug
def message(message):
    data = {'action': 'msg',
            'time': get_current_time(),
            'user': {'account_name': username,
                     'msg': message}
            }
    if message != '':
        return data


@decor_log_debug
def send_data(data):
    log.info('Data to send: %s', data)
    try:
        client_socket.send(encode_msg(data))
    except Exception:
        return None


@decor_log_debug
def get_data():
    while True:
        try:
            msg = decode_msg(client_socket.recv(BUFSIZ))
            if msg:
                parse_msg(msg)
        except OSError:
            log.exception('OSError in get_data')
            client_socket.close()
            break


@decor_log_debug
def parse_msg(msg):
    try:
        if msg['info'] == 'connect':
            print(f'User {msg["name"]} connected.')
        if msg['info'] == 'message':
            print(f'{msg["from"]}: {msg["message"]}')
        if msg['info'] == 'disconnect':
            print(f'User {msg["name"]} left.')
        if msg['response'] == 200:  # TODO check message delivery
            pass
    except KeyError:  # TODO переделать на нормальную обработку
        log.exception('KeyError in parse_msg() with message: %s', msg)


@decor_log_debug
def text_message():
    msg = ''
    try:
        msg = input()
    except KeyboardInterrupt:
        client_socket.close()
        exit('Bye-bye. See you soon.')
        log.exception('KeyboardInterrupt found. Exiting.')
    if msg == '':
        pass
    else:
        return send_data(message(msg))


if __name__ == '__main__':

    HOST = args.addr
    PORT = args.port
    BUFSIZ = 1024
    ADDR = (HOST, PORT)

    log.info('Parameters - addr: %s, message buffer: %d, %s:%s', ADDR, BUFSIZ, username, password)

    client_socket = socket(AF_INET, SOCK_STREAM)
    try:
        client_socket.connect(ADDR)
    except ConnectionRefusedError:
        log.exception("Can't connect. Connection refused")
        client_socket.close()
        exit("Can't connect. Connection refused")
    receive_thread = Thread(target=get_data)
    receive_thread.start()
    print(f'Connected to {HOST}:{PORT} as "{username}"')
    log.info('Connected to %s:%d as %s', HOST, PORT, username)
    send_data(presence(username))
    while True:
        try:
            text_message()
        except Exception:
            client_socket.close()
            break
