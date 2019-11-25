import datetime
import os
from bisect import bisect_left

import pandas
import phonenumbers

nums_df, lower_bounds = None, None

csv_urls = [
    'https://rossvyaz.ru/data/ABC-4xx.csv',
    'https://rossvyaz.ru/data/DEF-9xx.csv',
    'https://rossvyaz.ru/data/ABC-8xx.csv',
    'https://rossvyaz.ru/data/DEF-9xx.csv',
]


class NumberNotFound(Exception):
    def __init__(self, num):
        super().__init__(f'Телефон "{num}" не найден в базе данных Россвязи')


class NumberNotRecognized(Exception):
    def __init__(self, num):
        super().__init__(f'Телефон "{num}" не может быть распознан')


def csv_url_to_df(url):
    return pandas.read_csv(url,
                           delimiter=';',
                           names=['code', 'begin', 'end', 'count', 'operator', 'region'],
                           dtype={'code': str, 'begin': str, 'end': str})


def update_nums_df():
    dataframes = [csv_url_to_df(url) for url in csv_urls]
    df = pandas.concat(dataframes, ignore_index=True)

    df['begin'] = df['code'] + df['begin']
    df['end'] = df['code'] + df['end']
    df = df.drop('code', axis=1)

    df.to_hdf('data.h5', key='df', mode='w')

    global numsu_df, lower_bounds
    nums_df, lower_bounds = df, df['begin']

    print('Information updated:', datetime.datetime.now())
    return df


def get_nums_df(update=False):
    global nums_df
    if update or not os.path.exists('data.h5'):
        nums_df = update_nums_df()
    elif nums_df is None:
        nums_df = pandas.read_hdf('data.h5', 'df')

    return nums_df


def get_lower_bounds():
    global lower_bounds
    if lower_bounds is None:
        lower_bounds = get_nums_df()['begin']

    return lower_bounds


def parse_num(num):
    try:
        return phonenumbers.parse(num, 'RU')
    except phonenumbers.NumberParseException as e:
        raise NumberNotRecognized(num)


def get_num_info(num):
    num = parse_num(num)
    num_str = str(num.national_number)
    if len(num_str) != 10:
        raise NumberNotFound(num_str)
    lower_bound_i = bisect_left(get_lower_bounds(), num_str)
    if lower_bound_i == 0 or lower_bound_i == len(get_lower_bounds()):
        raise NumberNotFound(num_str)

    num_info = get_nums_df().iloc[lower_bound_i]
    if num_str > num_info['end']:
        raise NumberNotFound(num_str)

    response = {
        'Телефон': '7' + num_str,
        # 'Телефон': phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.NATIONAL),
        'Оператор': num_info['operator'],
        'Регион': num_info['region'],
        # 'from': num_info['begin'],
        # 'to': num_info['end'],
    }
    return response
