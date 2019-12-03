import csv
from io import StringIO
from multiprocessing.pool import ThreadPool

import pandas
import phonenumbers
import requests
from bs4 import BeautifulSoup
from constance import config

from rossvyaz.models import Region, Operator, Phone

rossvyaz_url = 'https://rossvyaz.ru/deyatelnost/resurs-numeracii/vypiska-iz-reestra-sistemy-i-plana-numeracii'
csv_urls = [
    'https://rossvyaz.ru/data/ABC-3xx.csv',
    'https://rossvyaz.ru/data/ABC-4xx.csv',
    'https://rossvyaz.ru/data/ABC-8xx.csv',
    'https://rossvyaz.ru/data/DEF-9xx.csv',
]


class NumberNotFound(Exception):
    def __init__(self, num):
        super().__init__(f'Телефон "{num}" не найден в базе данных Россвязи')


class NumberNotRecognized(Exception):
    def __init__(self, num):
        super().__init__(f'Телефон "{num}" не может быть распознан')


def write_string_io(df=None, columns=None, values=None):
    df = df if df is not None else None
    columns = columns or df.columns
    values = values or df.values
    s_buf = StringIO()
    writer = csv.writer(s_buf)
    writer.writerow(columns)
    writer.writerows(values)
    s_buf.seek(0)
    return s_buf


def get_rossvyaz_data_info():
    rossvyaz_html = requests.get(rossvyaz_url).content
    soup = BeautifulSoup(rossvyaz_html, "html.parser")
    update_date_selection = soup.select('body > div.page.page--grey > div > div.container-fluid.wrapper > '
                                        'p:nth-child(2) > strong')
    update_date = update_date_selection[0].text

    records_selection = soup.select('div.fields-container > div.paragraph-min.color-gray')
    records = records_selection[0].text.strip().split(' ')[-1]
    data_is_updated = update_date != config.rossvyaz_update_date or records != config.rossvyaz_records
    return update_date, records, data_is_updated


def fetch_csv(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise ConnectionError(f'{url} not downloaded correctly: {response.status_code}')
    return response.content


def fetch_all_csvs():
    pool = ThreadPool(4)
    results = pool.imap_unordered(fetch_csv, csv_urls)
    pool.close()
    pool.join()

    strings = [result.decode("utf-8") for result in results]
    csv_file = StringIO(''.join(strings))

    return csv_file


def prepare_df(csv_file):
    df = pandas.read_csv(
        csv_file,
        delimiter=';',
        names=['code', 'begin', 'end', 'count', 'operator', 'region'],
        dtype={'code': str, 'begin': str, 'end': str},
    )

    df['begin'] = df['code'] + df['begin']
    df['end'] = df['code'] + df['end']
    df = df.drop(['code', 'count'], axis=1)

    wrong_moscow_region = df[df['region'].str.startswith('Московская область')]
    df.at[wrong_moscow_region.index, 'region'] = 'г. Москва и Московская область'

    return df


def update_df_and_model(df, Model, column):
    db_names = set(Model.objects.values_list('name', flat=True))
    unique_names = [
        [name] for name in df[column].unique()
        if name not in db_names
    ]

    if len(unique_names) > 0:
        s_buf = write_string_io(columns=['name'], values=unique_names)
        Model.objects.from_csv(s_buf)

    name_to_id = dict(Model.objects.values_list('name', 'id'))
    df[column] = df[column].apply(lambda obj: name_to_id[obj])


def update_info(force=False):
    print('Updating information from rossvyaz.ru.')
    try_num = 0

    update_date, records, data_is_updated = get_rossvyaz_data_info()
    while (data_is_updated or force or not Phone.objects.exists()) and try_num < 5:
        force = False

        csv_file = fetch_all_csvs()
        df = prepare_df(csv_file)

        update_df_and_model(df, Operator, 'operator')
        update_df_and_model(df, Region, 'region')

        s_buf = write_string_io(df, columns=['begin', 'end', 'operator_id', 'region_id'])
        Phone.objects.from_csv(s_buf, replace=True)

        config.rossvyaz_update_date, config.rossvyaz_records = update_date, records

        update_date, records, data_is_updated = get_rossvyaz_data_info()
        try_num += 1

    if try_num >= 5:
        raise ValueError('Обновление данных не завершено')

    print(f'Information is up to date: {update_date} | {records} records')


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

    num_info = Phone.find(num_str)

    if num_info is None:
        raise NumberNotFound(num_str)

    response = {
        'number': '7' + num_str,
        # 'Телефон': phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.NATIONAL),
        'operator': num_info.operator.name,
        'region': num_info.region.name,
        # 'from': num_info['begin'],
        # 'to': num_info['end'],
    }
    return response
