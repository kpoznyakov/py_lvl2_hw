from socket import *
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--addr', type=str, help="IP to listen", default='')
parser.add_argument('port', type=int, help="port to listen", default=7777)
args = parser.parse_args()

registered_users = ['test']


def get_data():
    return json.loads(sock.recv(1024).decode("utf-8"))


def handle_authenticate(request):
    name = request['user']['account_name']
    if request['user']['account_name'] in registered_users:
        if request['user'] == {'account_name': 'test', 'password': 'test1'}:
            return {'response': 200, 'description': 'Login success!'}

        return {'response': 402, 'error': 'User found! Wrong password'}

    return {'response': 200, 'description': f'Login as unregistered user with name {name}'}


def handle_presence(request):
    acc = request['user']['account_name']
    if request['user']['status'] == 'OK':
        print(f'Client {acc} is there.')
        return {'response': 202, 'description': f'Client {acc} is there.'}

    return {'response': 404}


def handle_msg(request):
    return {'response': 200, 'message': request['user']['msg'], 'from': request['user']['account_name']}


def handler(request):
    print(f'Client sent {request}')
    response = mapping[request['action']](request)
    print(f'Response: {response}')
    return response


mapping = {
    'authenticate': handle_authenticate,
    'presence': handle_presence,
    'msg': handle_msg
}

with socket(AF_INET, SOCK_STREAM) as sock:
    sock.bind((args.addr, args.port))
    sock.listen(15)

    while True:
        conn, addr = sock.accept()

        with conn:
            print(f"Получен запрос на соединение от {addr}")
            data_b = conn.recv(1000000)
            print(data_b)
            data = json.loads(data_b, encoding='utf-8')
            response = handler(data)
            conn.send(json.dumps(response).encode('utf-8'))
