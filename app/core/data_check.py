import os
from datetime import timedelta
from dotenv import load_dotenv
from app.core.barcode_recognizer import barcode_handler
from app.schemas.validation_models import Report
from app.core.convertations import convert_str_to_datetime
from geopy.distance import geodesic
from app.models.shop_models import DATABASE


class BarcodeDataCheck:
    '''Класс, представляющий anti-fraud систему для защиты от подлога'''

    @staticmethod
    def time_check(report):
        '''Проверка на время'''

        time_limit = int(os.getenv('HOURS_LIMIT')) #Лимит на время из .env

        if abs(report.t - report.date_and_time) <= timedelta(hours=time_limit):
            return True
        raise Exception('Дата и время просрочены')


    @staticmethod
    def distance_check(report):
        '''Проверка на расстояние'''

        distance_limit = int(os.getenv('DISTANCE_LIMIT'))  #Лимит на дистанцию из .env

        for item in DATABASE:
            flag = False
            if item[0] == report.shop_id and item[1] == report.fn:
                if geodesic(item[2], report.gps) <= 2:
                    return True
                else:
                    raise Exception('Дистанция слишком большая')
            if not flag:
                raise Exception('Магазин не найден')


    def is_a_check_valid(self, report):
        '''Проверка информации из чека на достоверность'''

        load_dotenv()  #Используется, чтобы из .env можно было подгрузить данные о лимитах
        self.time_check(report)
        self.distance_check(report)

    async def review(
            self,
            barcode_img,
            date_and_time,
            gps,
            employee_id,
            shop_id,
    ):

        # Извлечение информации из штрихкода и возврат в виде словаря
        barcode_data = await barcode_handler(barcode_img)

        try:
            # Получение провалидированного объекта Pydantic модели Report
            report = Report(
                date_and_time=date_and_time,
                gps=gps,
                employee_id=employee_id,
                shop_id=shop_id,
                t=convert_str_to_datetime(barcode_data['t']),
                s=barcode_data['s'],
                fn=barcode_data['fn'],
                i=barcode_data['i'],
                fp=barcode_data['fp'],
                n=barcode_data['n'],
            )

            # Проверка на подделку и актуальность
            try:
                self.is_a_check_valid(report)
                return 'Принято'
            except Exception as err:
                return f'Не принято {err}'

        except Exception:
            return 'Ошибка при распознании или данные некорректны'