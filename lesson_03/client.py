from socket import *
import json
import argparse
import datetime

TIME = str(datetime.datetime.now().replace(microsecond=0).isoformat(sep=' '))

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--addr', type=str, help="IP to connect", default='localhost')
parser.add_argument('--port', type=int, help="port to connect", default=7777)
parser.add_argument('-u', '--user', type=str, help="username",
                    default='defaultuser_' + str(datetime.datetime.now().timestamp()))
parser.add_argument('-p', '--password', type=str, help="password")
args = parser.parse_args()

# username = args.user
# password = args.password
username = 'test'
password = 'test1'


def auth():
    auth_msg = {
        'action': 'authenticate',
        'time': TIME,
        'user': {'account_name': username,
                 'password': password}
    }
    return auth_msg


def presence():
    presence_msg = {
        'action': 'presence',
        'time': TIME,
        'type': 'status',
        'user': {'account_name': username,
                 "status": "OK"}
    }
    return presence_msg


def message(message):
    data = {'action': 'msg',
            'time': TIME,
            'user': {'account_name': username,
                     'msg': message}
            }
    return data


def send_data(data):
    s.send(json.dumps(data).encode('utf-8'))


def get_data():
    data = json.loads(s.recv(1000000).decode('utf-8'))
    if data['response'] == 402:
        s.close()
        exit('Wrong password')
    print('Сообщение от сервера: ', data)
    return data


with socket(AF_INET, SOCK_STREAM) as s:
    s.connect((args.addr, args.port))
    # send_data(auth())
    # print(get_data())
    send_data(presence())

    while True:
        get_data()
        send_data(message(input('Your message: ')))
