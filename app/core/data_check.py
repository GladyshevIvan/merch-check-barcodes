from datetime import timedelta, datetime
import asyncio
from typing import Tuple
from uuid import UUID
from fastapi import UploadFile
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
    def time_check(report: Report) -> bool:
        '''
        Проверка времени в отчете на актуальность

        Сравнивает время отчета и время в чеке, если они отличаются больше, чем на лимит, установленный в .env,
        возбуждается исключение, иначе возвращается True

        Args:
            report (Report): Объект Pydantic-модели Report, с данными отчета, включая время
        Returns:
            bool: True, если разница во времени находится в пределах лимита
        Raises:
            Exception: Если разница во времени превышает лимит, указанный в HOURS_LIMIT из .env
        '''

        time_limit = int(settings.HOURS_LIMIT) #Лимит на время из переменной окружения HOURS_LIMIT

        if abs(report.t - report.date_and_time) <= timedelta(hours=time_limit):
            return True
        raise Exception('Дата и время просрочены')


    @staticmethod
    async def distance_check(report: Report) -> bool:
        '''
        Проверяет расстояние между местоположением отчета и местоположением магазина

        Вычисляет расстояние между GPS-координатами, указанными в отчете, и координатами
        магазина, полученными из Базы Данных. Проверяет, находится ли это расстояние в пределах лимита

        Args:
            report (Report): Объект Pydantic-модели Report, с данными отчета, включая GPS-координаты и shop_id
        Returns:
            bool: True, если расстояние между местоположением отчета и магазина находится в пределах лимита
        Raises:
            Exception: Если расстояние между местоположениями отправки отчета и магазина превышает лимит
            Exception: Если магазин не найден в Базе Данных
        '''

        distance_limit = int(settings.DISTANCE_LIMIT)  #Лимит на дистанцию из переменной окружения DISTANCE_LIMIT

        async with async_session_maker() as session:

            #Создание объекта репозитория с отдельной сессией для операций с Базой Данных
            repository = SqlAlchemyCheckReviewRepository(session)

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
    async def check_dublicats(report: Report) -> bool:
        '''
        Проверяет наличие дубликатов чеков в Базе Данных

        Проверяет, существует ли чек с такими же 'fp' и 'fn', а затем с такими же 't', 'fn' и 'i'
        в базе данных

        Args:
            report (Report): Объект Pydantic-модели Report с данными отчета
        Returns:
            bool: True, если дубликаты не найдены
        Raises:
            Exception: Если чек с такими же данными уже существует в Базе Данных
        '''

        async with async_session_maker() as session_fp_fn, async_session_maker() as session_t_fn_i:

            #Создание объектов репозитория с отдельной сессией для операций с Базой Данных
            repository_fp_fn_check = SqlAlchemyCheckReviewRepository(session_fp_fn)
            repository_t_fn_i_check = SqlAlchemyCheckReviewRepository(session_t_fn_i)

            fp_fn_dublicates, t_fn_i_dublicates = await asyncio.gather(
                                                                        repository_fp_fn_check.get_fp_fn(fp=report.fp, fn=report.fn,),
                                                                        repository_t_fn_i_check.get_t_fn_i(t=report.t, fn=report.fn, i=report.i)
                                                                        )

            #Проверка есть ли чек с такими же 'fp', 'fn', затем проверка на совпадение 't', 'fn' и 'i'
            if fp_fn_dublicates or t_fn_i_dublicates:
                #Если чек найден, вылетает исключение
                raise Exception('Этот чек уже загружен в Базу Данных')

            #Если чека нет в Базе Данных
            return True


    @staticmethod
    async def add_check_to_db(report: Report) -> None:
        '''
        Добавляет данные чека в таблицу used_checks

        Args:
            report (Report): Объект Pydantic-модели Report с данными отчета
        Returns:
            None
        '''

        async with async_session_maker() as session:

            #Создание объекта репозитория с отдельной сессией для операций с Базой Данных
            repository = SqlAlchemyCheckReviewRepository(async_session_maker())

            await repository.add_used_check(fp=report.fp, fn=report.fn, t=report.t, i=report.i)

    @staticmethod
    async def add_task_to_db(report: Report) -> None:
        '''
        Добавление в Базу Данных записи о том, что сотрудник выполнил задачу для магазина с shop_id такого-то числа

        Args:
            report (Report): Объект Pydantic-модели Report с данными отчета
        Returns:
            None
        '''

        async with async_session_maker() as session:
            # Создание объекта репозитория с отдельной сессией для операций с Базой Данных
            repository = SqlAlchemyCheckReviewRepository(async_session_maker())

            await repository.add_completed_task(employee_id=report.employee_id, shop_id=report.shop_id, date_and_time=report.date_and_time)


    async def is_a_check_valid(self, report: Report):
        '''
        Проверка информации из чека на достоверность

        Происходит проверка на отклонение времени отправки отчета со временем в чеке,
        проверяется наличие чека в Базе Данных,
        проверяется отклонение по расстоянию между GPS-координатами магазина и GPS-координатами точки отправки отчета.

        Если все в порядке, чек добавляется в Базу Данных, а так же в нее вносится запись о выполненной работе

        Args:
            report (Report): Объект Pydantic-модели Report, содержащий данные отчета
        Returns:
            None
        Raises:
            Exception: Если какая-либо из проверок не пройдена
        '''

        #Проверка на время
        self.time_check(report)

        #Проверка чека на наличие в Базе Данных, а затем на расстояние
        await asyncio.gather(
            self.check_dublicats(report),
            self.distance_check(report)
        )

        #Вызов функции для добавления чека в Базу данных
        await self.add_check_to_db(report)

        #Вызов функции для добавления записи о выполненной работе в Базу Данных
        await self.add_task_to_db(report)


    async def review(
            self,
            barcode_img: UploadFile,
            date_and_time: datetime,
            gps: Tuple[float, float],
            employee_id: UUID,
            shop_id: UUID,
    ):
        '''
        Функция, которая проверяет данные из запроса и штрихкода на достоверность

        Извлекает информацию из изображения штрихкода и преобразует ее в словарь,
        На основе переданных в запросе данных и данных из словаря, создает Pydantic-модель Report,
        валидирующую данные
        Далее с помощью функции is_a_check_valid полученный экземпляр класса report проверяются на достоверность

        Args:
            - barcode_img (UploadFile): Изображение штрихкода
            - date_and_time (datetime): Дата и время отчета
            - gps (Tuple[float, float]): GPS-координаты (широта, долгота) места откуда отправили отчет в виде кортежа
            - employee_id (UUID): Идентификатор сотрудника
            - shop_id (UUID): Идентификатор магазина
        Returns:
            str: Сообщение о результате проверки: 'Принято' или сообщение об ошибке
        '''

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