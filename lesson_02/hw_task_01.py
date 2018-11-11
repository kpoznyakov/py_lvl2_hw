# 1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку определенных данных из файлов
# info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV. Для этого:
# Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными,
# их открытие и считывание данных.
#
# В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь
# значения параметров
# «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
# Значения каждого параметра поместить в соответствующий список.
#
# Должно получиться четыре списка — например,
# os_prod_list, os_name_list, os_code_list, os_type_list.
#
# В этой же функции создать главный список для хранения данных отчета — например, main_data — и поместить в него
# названия столбцов отчета в виде списка:
# «Изготовитель системы»,
# «Название ОС»,
# «Код продукта»,
# «Тип системы».
# Значения для этих столбцов также оформить в виде списка и поместить в файл main_data (также для каждого файла);
# Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой функции реализовать получение
# данных через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий CSV-файл;
# Проверить работу программы через вызов функции write_to_csv().
#

import os
import chardet
import csv
import re

EXT_TO_FIND = '.txt'  # can be a ('.py', '.txt', '.jpg', '.etc')
PATH_TO_FILES = './'

files_list = []

os_prod_list = []
os_name_list = []
os_code_list = []
os_type_list = []

main_data = {
    'Изготовитель системы': [],
    'Название ОС': [],
    'Код продукта': [],
    'Тип системы': []
}


def find_files(path):  # find files with extension EXT_TO_FIND
    for root, _, files in os.walk(path):
        for filename_ in files:
            basename, ext = os.path.splitext(filename_)
            if ext.lower() in EXT_TO_FIND:
                files_list.append(basename + ext)
    # print(files_list)


# вся эта заморочка связана с тем что я на маке, а файлы в кодировке windows-1251. Решил автоматизировать

def get_encoding(f):
    with open(f, 'rb') as bd:
        return chardet.detect(bd.read())['encoding']


def get_data(file):
    for el in file:
        with open(el, 'r', encoding=get_encoding(el)) as f:
            data = f.read()
            # print(data)
            for k, v in main_data.items():
                val = re.search(f'{k}:(.*)', data)
                # print(str(val))
                if val:
                    v.append(val.group(1).strip())
    return main_data


def write_to_csv(filename):
    report = get_data(filename)
    # print(report)
    with open('result_task_1.csv', 'w') as f_n:
        writer = csv.DictWriter(f_n, report.keys())
        writer.writeheader()
        for i in range(len(files_list)):
            writer_dict = {}
            for key, value in report.items():
                writer_dict.update({key: value[i]})
            writer.writerow(writer_dict)

find_files(PATH_TO_FILES)
# print(files_list)

write_to_csv(files_list)
