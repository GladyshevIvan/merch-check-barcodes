from datetime import timedelta
import asyncio
from geopy.distance import geodesic
from app.config import settings
from app.core.barcode_recognizer import barcode_handler
from app.schemas.validation_models import Report
from app.core.convertations import convert_str_to_datetime
from app.repositories.check_review_repository import SqlAlchemyCheckReviewRepository
from app.db.database import async_session_maker


class BarcodeDataCheck:
    '''Класс, представляющий anti-fraud систему для защиты от подлога'''


    @staticmethod
    def time_check(report):
        '''Проверка на время'''

        time_limit = int(settings.HOURS_LIMIT) #Лимит на время из .env

        if abs(report.t - report.date_and_time) <= timedelta(hours=time_limit):
            return True
        raise Exception('Дата и время просрочены')


    @staticmethod
    async def distance_check(report):
        '''Проверка на расстояние'''

        distance_limit = int(settings.DISTANCE_LIMIT)  #Лимит на дистанцию из .env

        #Создание объекта репозитория с отдельной сессией для операций с Базой Данных
        repository = SqlAlchemyCheckReviewRepository(async_session_maker())

        #Вызов у репозитория метода для извлечения координат из Базы Данных
        shop_db_data = await repository.get_shop_cords(shop_id=report.shop_id, fn=report.fn)

        if shop_db_data: #Если магазин с такими полями есть
            gps_from_db = (shop_db_data.latitude, shop_db_data.longitude) #Получение gps по этим ключам

            if geodesic(gps_from_db, report.gps) <= distance_limit:
                return True
            else:
                raise Exception('Дистанция слишком большая')
        else:
            raise Exception('Магазин не найден')


    @staticmethod
    async def check_dublicats(report):
        '''Проверка по 'fp', 'fn', а затем по 't', 'fn' и 'i' чек на наличие в Базе Данных'''

        #Создание объектов репозитория с отдельной сессией для операций с Базой Данных
        repository_fp_fn_check = SqlAlchemyCheckReviewRepository(async_session_maker())
        repository_t_fn_i_check = SqlAlchemyCheckReviewRepository(async_session_maker())

        fp_fn_dublicates, t_fn_i_dublicates = await asyncio.gather(
                                                                    repository_fp_fn_check.get_fp_fn(fp=report.fp, fn=report.fn,),
                                                                    repository_t_fn_i_check.get_t_fn_i(t=report.t, fn=report.fn, i=report.i)
                                                                    )

        #Проверка есть ли чек с такими же 'fp', 'fn', затем проверка на совпадение 't', 'fn' и 'i'
        if fp_fn_dublicates or t_fn_i_dublicates:
            #Если чек найден, вылетает исключение
            raise Exception('Этот чек уже загружен в Базу Данных')


    @staticmethod
    async def add_check_to_db(report):
        '''Добавление чека в таблицу used_checks'''

        #Создание объекта репозитория с отдельной сессией для операций с Базой Данных
        repository = SqlAlchemyCheckReviewRepository(async_session_maker())

        await repository.add_used_check(fp=report.fp, fn=report.fn, t=report.t, i=report.i)


    async def is_a_check_valid(self, report):
        '''Проверка информации из чека на достоверность'''

        #Проверка на время
        self.time_check(report)

        #Проверка чека на наличие в Базе Данных, а затем на расстояние
        await asyncio.gather(
            self.check_dublicats(report),
            self.distance_check(report)
        )

        #Вызов функции для добавления чека в Базу данных
        await self.add_check_to_db(report)


    async def review(
            self,
            barcode_img,
            date_and_time,
            gps,
            employee_id,
            shop_id,
    ):


        try:
            #Извлечение информации из штрихкода и возврат в виде словаря
            barcode_data = await barcode_handler(barcode_img)

            #Получение провалидированного объекта Pydantic модели Report
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

            #Проверка на подделку и актуальность
            try:
                await self.is_a_check_valid(report)
                return 'Принято'
            except Exception as err:
                return f'Не принято {err}'

        except Exception:
            return 'Ошибка при распознании или данные некорректны'