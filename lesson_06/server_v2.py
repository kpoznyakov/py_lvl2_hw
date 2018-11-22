import socket
import json
import argparse
import inspect
from threading import Thread
from log.server_log_config import *

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--addr', type=str, help="IP to listen", default='')
parser.add_argument('--port', type=int, help="port to listen", default=7777)
parser.add_argument('--debug', type=bool, help='debug flag', default=True)
args = parser.parse_args()

clients = {}
registered_users = ['test']
debug = args.debug


def caller_name(skip=2):  # from https://gist.github.com/techtonik/2151727
    """Get a name of a caller in the format module.class.method

       `skip` specifies how many levels of stack to skip while getting caller
       name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

       An empty string is returned if skipped levels exceed stack height
    """
    stack = inspect.stack()
    start = 0 + skip
    if len(stack) < start + 1:
        return ''
    parentframe = stack[start][0]

    name = []
    module = inspect.getmodule(parentframe)
    # `modname` can be None when frame is executed directly in console
    # TODO(techtonik): consider using __main__
    if module:
        name.append(module.__name__)
    # detect classname
    if 'self' in parentframe.f_locals:
        # I don't know any way to detect call from the object method
        # XXX: there seems to be no way to detect static method call - it will
        #      be just a function call
        name.append(parentframe.f_locals['self'].__class__.__name__)
    codename = parentframe.f_code.co_name
    if codename != '<module>':  # top level usually
        name.append(codename)  # function or a method
    del parentframe
    return ".".join(name)


def decor_log_debug(func):
    if debug:
        def wrapper(*args, **kwargs):
            caller = caller_name(2)
            log.debug('Func "%s" from "%s" got "%s", "%s"', func.__name__, caller, args, kwargs)
            r = func(*args, **kwargs)
            return r

        return wrapper
    else:
        return func


@decor_log_debug
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


@decor_log_debug
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


@decor_log_debug
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


@decor_log_debug
def send_broadcast_msg(msg, client):
    for sock in clients:
        if sock != client:
            sock.send(encode_msg(msg))
            log.debug('SEND message %s to %s', msg, sock)
        if sock == client:
            sock.send(encode_msg({'response': 200}))
            log.debug('SEND message {"response": 200} to %s', sock)


@decor_log_debug
def decode_msg(data_b):  # TODO вынести в файл общего кода
    return json.loads(data_b, encoding='utf-8')


@decor_log_debug
def encode_msg(data):  # TODO вынести в файл общего кода
    return json.dumps(data).encode('utf-8')


@decor_log_debug
def check_handler(data):
    try:
        response = handlers[data['action']](data)
    except Exception:
        log.exception('Exception in check_handler')
        return None
    return response


@decor_log_debug
def handle_authenticate(request):
    name = request['user']['account_name']
    if request['user']['account_name'] in registered_users:  # TODO вынести в функцию проверки реги
        if request['user'] == {'account_name': 'test', 'password': 'test1'}:
            return {'response': 200, 'description': 'Login success!'}
        return {'response': 402, 'error': 'User found! Wrong password'}
    return {'response': 200, 'description': f'Login as unregistered user with name {name}'}


@decor_log_debug
def handle_presence(request):
    acc = request['user']['account_name']
    if request['user']['status'] == 'OK':
        log.info(f'Client {acc} is there.')
        return {'response': 202, 'description': f'Client {acc} is there.'}


@decor_log_debug
def handle_msg(request):
    return {'info': 'message', 'message': request['user']['msg'], 'from': request['user']['account_name']}


handlers = {
    'authenticate': handle_authenticate,
    'presence': handle_presence,
    'msg': handle_msg
}

if __name__ == "__main__":
    threaded_server(args.addr, args.port)
