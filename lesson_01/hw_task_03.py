# 3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.


s_1 = b'attribute'
s_2 = b'класс'
s_3 = b'функция'
s_4 = b'type'

#     s_2 = b'класс'
#          ^
# SyntaxError: bytes can only contain ASCII literal characters.

#     s_3 = b'функция'
#          ^
# SyntaxError: bytes can only contain ASCII literal characters.
