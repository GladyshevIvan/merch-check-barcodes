from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import pytz
from app.config import settings


def convert_str_to_datetime(date_str):
    '''Преобразование строки в дату'''

    if date_str.endswith('Z'):
        #Попытка распарсить строку с 'Z'
        date_object = datetime.strptime(date_str[:-1], '%Y%m%dT%H%M%S')
        localized_datetime = pytz.utc.localize(date_object) #Если есть Z, устанавливается пояс UTC
        return localized_datetime
    else:
        try:
            #Если нет Z, проверка, указан ли поясесли +HHMM или -HHMM нет, тогда указывается пояс из .env
            for sign in ('+', '-'):
                if sign in date_str:
                    date_part, timezone_part = date_str.split(sign)
                    date_object = datetime.strptime(date_part, '%Y%m%dT%H%M%S')

                    timezone_hours = int(timezone_part[:2])
                    timezone_minutes = int(timezone_part[2:])

                    modificator = 1 if sign == '+' else -1

                    offset = timedelta(hours=modificator * timezone_hours, minutes=modificator * timezone_minutes)
                    tz = timezone(offset)

                    localized_datetime = date_object.replace(tzinfo=tz)

                    return localized_datetime

            #Если пояс не указан
            load_dotenv()
            time_zone = pytz.timezone(settings.TIME_ZONE) # Загрузка часового пояса из .env
            date_object = datetime.strptime(date_str, '%Y%m%dT%H%M%S')
            localized_datetime = time_zone.localize(date_object)
            return localized_datetime

        except ValueError:
            raise ValueError('Неверный формат даты и времени (ожидается YYYYMMDDTHHMMSS+HHMM , YYYYMMDDTHHMMSS-HHMM или YYYYMMDDTHHMMSS[Z])')


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