# 4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления
# в байтовое и выполнить обратное преобразование (используя методы encode и decode).


words = ("разработка", "администрирование", "protocol", "standard")

for word in words:
    temp_word = word.encode()
    print(temp_word)
    print(temp_word.decode('utf-8'))
    print("*" * 10)
   