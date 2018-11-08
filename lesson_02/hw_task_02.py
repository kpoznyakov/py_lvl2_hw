# ### 2. Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON
# с информацией о заказах. Написать скрипт, автоматизирующий его заполнение данными.
# Для этого:
# Создать функцию write_order_to_json(), в которую передается 5 параметров —
# товар (item),
# количество (quantity),
# цена (price),
# покупатель (buyer),
# дата (date).

# Функция должна предусматривать запись данных в виде словаря в файл orders.json.
# При записи данных указать величину отступа в 4 пробельных символа;
# Проверить работу программы через вызов функции write_order_to_json() с передачей в нее значений каждого параметра.
#


import json
import datetime


def write_order_to_json(filename, item, quantity, price, buyer, date):
    input_data = {
        'id': 0,
        'item': item,
        'quantity': quantity,
        'price': price,
        'buyer': buyer,
        'date': date
    }

    with open(filename, 'r') as infile:
        feeds = json.load(infile)

    try:
        input_data['id'] = feeds['orders'][-1]['id'] + 1
    except IndexError:
        input_data['id'] = 0
    feeds['orders'].append(input_data)

    with open('orders.json', 'w') as outfile:
        # print(feeds)
        outfile.write(json.dumps(feeds, indent=4))


write_order_to_json('orders.json', 'Apple', 10, 14, 'Jobs',
                    datetime.datetime.now().strftime("%H:%M:%S.%f on %B %d, %Y"))
