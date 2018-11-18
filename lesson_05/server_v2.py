import socket
import json
import argparse
from threading import Thread
from log.server_log_config import *

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--addr', type=str, help="IP to listen", default='')
parser.add_argument('--port', type=int, help="port to listen", default=7777)
args = parser.parse_args()

clients = {}
registered_users = ['test']


def threaded_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if host == '':
            host = 'localhost'
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(100)
        print(f'Server listen on {host}:{port}')
        log.info('Server listen on %s:%d', host, port)
        accept_thread = Thread(target=accept_incoming_connections, args=(server,))
        accept_thread.start()
        accept_thread.join()
    except KeyboardInterrupt:
        print('Server stopped by user')
        log.warning('Server stopped by user')
    except Exception:
        log.critical('Something bad happens!')
    finally:
        server.close()
        log.info('Close connection')


def accept_incoming_connections(sock):
    while True:
        try:
            client, client_address = sock.accept()
            log.info('CONNECT %s %s', client, client_address)
            Thread(target=handle_client, args=(client,)).start()
        except ConnectionAbortedError:
            log.exception('ConnectionAbortedError')
            break
        except OSError:
            log.exception('OSError')
            break


def handle_client(client):
    name = decode_msg(client.recv(1024))['user']['account_name']
    clients[client] = name
    send_broadcast_msg({'info': 'connect', 'name': name}, client)
    log.info('CLIENTS(%d): %s', len(clients), clients)
    while True:
        try:
            msg = decode_msg(client.recv(1024))
            log.debug('MESSAGE %s from %s', msg, name)
        except json.decoder.JSONDecodeError:
            send_broadcast_msg({'info': 'disconnect', 'name': clients.pop(client)}, client)
            log.info('DISCONNECT: %s', client)
            log.info('N of CLIENTS = %d', len(clients))
            log.warning('DISCONNECT: %s', client)
            break
        response = check_handler(msg)
        send_broadcast_msg(response, client)


def send_broadcast_msg(msg, client):
    log.debug('MESSAGE TO BROADCAST %s', msg)
    for sock in clients:
        if sock != client:
            sock.send(encode_msg(msg))
            log.debug('SEND message %s to %s', msg, sock)
        if sock == client:
            sock.send(encode_msg({'response': 200}))
            log.debug('SEND message {"response": 200} to %s', sock)


def decode_msg(data_b):  # TODO вынести в файл общего кода
    return json.loads(data_b, encoding='utf-8')


def encode_msg(data):  # TODO вынести в файл общего кода
    return json.dumps(data).encode('utf-8')


def check_handler(data):
    try:
        response = handlers[data['action']](data)
    except Exception:
        log.exception('Exception in check_handler')
        return None
    return response


def handle_authenticate(request):
    name = request['user']['account_name']
    if request['user']['account_name'] in registered_users:  # TODO вынести в функцию проверки реги
        if request['user'] == {'account_name': 'test', 'password': 'test1'}:
            return {'response': 200, 'description': 'Login success!'}
        return {'response': 402, 'error': 'User found! Wrong password'}
    return {'response': 200, 'description': f'Login as unregistered user with name {name}'}


def handle_presence(request):
    acc = request['user']['account_name']
    if request['user']['status'] == 'OK':
        log.info(f'Client {acc} is there.')
        return {'response': 202, 'description': f'Client {acc} is there.'}


def handle_msg(request):
    return {'info': 'message', 'message': request['user']['msg'], 'from': request['user']['account_name']}


handlers = {
    'authenticate': handle_authenticate,
    'presence': handle_presence,
    'msg': handle_msg
}

if __name__ == "__main__":
    threaded_server(args.addr, args.port)
