from datetime import datetime, timezone
import pytz


def convert_str_to_datetime(date_str):
    '''Преобразование строки в дату'''

    try:
        #Попытка распарсить строку с 'Z'
        return datetime.strptime(date_str, '%Y%m%dT%H%M%SZ').replace(tzinfo=pytz.utc)
    except ValueError:
        try:
            #Если не удалось, попытка распарсить строку без 'Z'
            date_object = datetime.strptime(date_str, '%Y%m%dT%H%M%S')
            return pytz.utc.localize(date_object)  #Установка UTC
        except ValueError:
            raise ValueError('Неверный формат даты и времени (ожидается YYYYMMDDTHHMMSS[Z])')


def convert_str_to_tuple(data_string):
    '''Преобразование data_string в Tuple[float, float]'''

    try:
        raw_gps_list = data_string[1:len(data_string) - 1].split(', ')
        return tuple(map(float, raw_gps_list))
    except:
        raise Exception('Неверный gps')


def convert_string_to_dict(barcode_data_string):
    '''Преобразование строки из штрихкода в словарь'''

    if barcode_data_string:
        barcode_data = {}
        for item in barcode_data_string.split('&'):
            key, value = item.split('=')
            barcode_data[key] = value

        return barcode_data
    else:
        raise Exception('Штрихкод в изображении не найден')