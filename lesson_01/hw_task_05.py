# 5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com
# и преобразовать результаты из байтовового в строковый тип на кириллице.

import subprocess

PING_LIMIT = "5"

resources = ['yandex.ru', 'youtube.com']

args = ["ping", "-c", PING_LIMIT, "127.0.0.1"]

for resource in resources:
    args[-1] = resource
    subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
    for line in subproc_ping.stdout:
        print(line)
        print(line.decode('utf-8'))
