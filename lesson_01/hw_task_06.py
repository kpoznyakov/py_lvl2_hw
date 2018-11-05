# 6. Создать текстовый файл test_file.txt, заполнить его тремя строками:
# «сетевое программирование», «сокет», «декоратор».
# Проверить кодировку файла по умолчанию. Принудительно открыть файл в формате Unicode и вывести его содержимое.

import chardet
import locale

print(locale.getdefaultlocale())
# ('en_US', 'UTF-8')

with open('file.txt', 'rb') as f:
    s = f.read()
    print(s)
    print(chardet.detect(s))

with open('file.txt', encoding='cp1251', errors='replace') as fl:
    print(fl.read())
