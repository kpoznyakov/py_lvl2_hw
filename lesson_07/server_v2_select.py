import socket
import json
import argparse
import inspect
import select
from log.server_log_config import *

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--addr', type=str, help="IP to listen", default='')
parser.add_argument('--port', type=int, help="port to listen", default=7777)
parser.add_argument('--debug', type=bool, help='debug flag', default=True)
args = parser.parse_args()
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


clients = {}
registered_users = ['test']
msg = {}
socket_clients = []


def select_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if host == '':
            host = 'localhost'
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(100)
        server.settimeout(0.2)
        print(f'Server listen on {host}:{port}')
        log.info('Server listen on %s:%d', host, port)

        while True:
            try:
                client, client_address = server.accept()
            except OSError as e:
                pass  # timeout вышел
            else:
                socket_clients.append(client)

            readable, writable, exceptional = select.select(socket_clients, socket_clients, [], 1)

            for c in readable:
                try:
                    handle_client(c, writable)
                except ConnectionResetError:
                    socket_clients.remove(c)
            for c in writable:
                try:
                    pass
                except BrokenPipeError:
                    print("Can't connect to client:", c)
            for c in exceptional:
                print('exceptional', c)
    except KeyboardInterrupt:
        print('Server stopped by user')
        log.warning('Server stopped by user')
    except Exception:
        log.critical('Something bad happens!')
    finally:
        server.close()
        log.info('Close connection server.close()')


@decor_log_debug
def handle_client(client, writable):
    data_b = client.recv(1024)
    message_from_client = decode_msg(data_b)
    for c in writable:
        c.send(encode_msg(message_from_client))


@decor_log_debug
def decode_msg(data_b):  # TODO вынести в файл общего кода
    if data_b == b'':
        return json.loads("{}", encoding='utf-8')
    return json.loads(data_b, encoding='utf-8')


@decor_log_debug
def encode_msg(data):  # TODO вынести в файл общего кода
    return json.dumps(data).encode('utf-8')


if __name__ == "__main__":
    select_server(args.addr, args.port)
