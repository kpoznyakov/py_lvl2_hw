from socket import *
import json
import argparse
import datetime
import time
from threading import Thread
from log.client_log_config import *


def get_current_time():
    return str(datetime.datetime.now().replace(microsecond=0).isoformat(sep=' '))


parser = argparse.ArgumentParser()
parser.add_argument('-a', '--addr', type=str, help="IP to connect", default='localhost')
parser.add_argument('--port', type=int, help="port to connect", default=7777)
parser.add_argument('-u', '--user', type=str, help="username",
                    default='username_' + get_current_time())
parser.add_argument('-p', '--password', type=str, help="password")
args = parser.parse_args()

username = args.user
password = args.password


def decode_msg(data_b):  # TODO вынести в файл общего кода
    return json.loads(data_b, encoding='utf-8')


def encode_msg(data):  # TODO вынести в файл общего кода
    return json.dumps(data).encode('utf-8')


def auth():
    auth_msg = {
        'action': 'authenticate',
        'time': get_current_time(),
        'user': {'account_name': username,
                 'password': password}
    }
    return auth_msg


def presence():
    presence_msg = {
        'action': 'presence',
        'time': get_current_time(),
        'type': 'status',
        'user': {
            'account_name': username,
            "status": "OK"
        }
    }
    return presence_msg


def message(message):
    data = {'action': 'msg',
            'time': get_current_time(),
            'user': {'account_name': username,
                     'msg': message}
            }
    if message != '':
        return data


def send_data(data):
    log.info('Data to send: %s', data)
    client_socket.send(encode_msg(data))


def get_data():
    while True:
        try:
            msg = decode_msg(client_socket.recv(BUFSIZ))
            log.debug('Message: %s', msg)
            if msg:
                parse_msg(msg)
        except OSError:
            log.exception('OSError in get_data')
            client_socket.close()
            break


def parse_msg(msg):
    try:
        if msg['response']:  # TODO check message delivery
            pass
    except KeyError:  # TODO переделать на нормальную обработку
        log.debug('KeyError in parse_msg() with message: %s', msg)
        if msg['info'] == 'connect':
            print(f'User {msg["name"]} connected.')
        if msg['info'] == 'message':
            print(f'{msg["from"]}: {msg["message"]}')
        if msg['info'] == 'disconnect':
            print(f'User {msg["name"]} left.')


def text_message():
    time.sleep(0.001)
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
        log.debug('User message: %s', msg)
        return send_data(message(msg))


if __name__ == '__main__':
    HOST = args.addr
    PORT = args.port
    BUFSIZ = 1024
    ADDR = (HOST, PORT)

    log.debug('Parameters - addr: %s, message buffer: %d, %s:%s', ADDR, BUFSIZ, username, password)

    client_socket = socket(AF_INET, SOCK_STREAM)
    try:
        client_socket.connect(ADDR)
    except ConnectionRefusedError:
        log.exception("Can't connect. Connection refused")
        client_socket.close()
        exit("Can't connect. Connection refused")
    receive_thread = Thread(target=get_data)
    receive_thread.start()
    print(f'Connected to {HOST}:{PORT} as {username}')
    log.info('Connected to %s:%d as %s', HOST, PORT, username)
    send_data(presence())
    while True:
        try:
            text_message()
        except Exception:
            client_socket.close()
            break
