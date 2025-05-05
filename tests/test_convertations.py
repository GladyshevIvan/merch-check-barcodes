from datetime import datetime, timezone, timedelta
import pytest
import pytz
from app.core.convertations import convert_str_to_datetime, convert_string_to_dict
from app.config import settings


#Параметры для проверки функции convert_str_to_datetime
@pytest.mark.parametrize(
    'date_str, expected_result',
    [
        ('20250423T201202Z', pytz.utc.localize(datetime(2025, 4, 23, 20, 12, 2))),
        ('20250423T201202', pytz.timezone(settings.TIME_ZONE).localize(datetime(2025, 4, 23, 20, 12, 2))),
        ('20250423T201202+0300', datetime(2025, 4, 23, 20, 12, 2, tzinfo=timezone(timedelta(hours=3)))),
        ('20250423T201202-0300', datetime(2025, 4, 23, 20, 12, 2, tzinfo=timezone(timedelta(hours=-3)))),
        ('20250423T201202+03', pytest.raises(ValueError)),
        ('20250423T201202-03', pytest.raises(ValueError)),
        ('', pytest.raises(ValueError))
    ]
)


def test_convert_str_to_datetime(date_str, expected_result):
    '''Проврка конвертации строки с датой в datetime-объект с часовым поясом'''

    if isinstance(expected_result, type(pytest.raises(ValueError))):
        with expected_result:
            convert_str_to_datetime(date_str)
    else:
        result = convert_str_to_datetime(date_str)
        assert result == expected_result


#Параметры для проверки функции convert_string_to_dict
@pytest.mark.parametrize(
    'barcode_data_string, expected_result',
    [
        ('t=20180412T102900&s=1800.00&fn=9999078900004658&i=171&fp=2256047510&n=1', {'t': '20180412T102900', 's': '1800.00', 'fn': '9999078900004658', 'i': '171', 'fp': '2256047510', 'n': '1'}),
        ('t=20180412T102900;s=1800.00;fn=9999078900004658', pytest.raises(Exception)),
        ('', pytest.raises(Exception))
    ]
)


def test_convert_barcode_data_string(barcode_data_string, expected_result):
    '''Проврка конвертации строки с датой в словарь'''

    if isinstance(expected_result, type(pytest.raises(Exception))):
        with expected_result:
            convert_string_to_dict(barcode_data_string)
    else:
        result = convert_string_to_dict(barcode_data_string)
        assert result == expected_result