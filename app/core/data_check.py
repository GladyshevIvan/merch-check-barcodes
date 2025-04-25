import os
from datetime import timedelta
from dotenv import load_dotenv
from geopy.distance import geodesic
from app.schemas.schemas import DATABASE


def time_check(report):
    '''Проверка на время'''

    time_limit = int(os.getenv('HOURS_LIMIT')) #Лимит на время из .env

    if report.t - report.date_and_time <= timedelta(hours=time_limit):
        return True
    raise Exception('Дата и время просрочены')


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


def is_a_check_valid(report):
    '''Проверка информации из чека на достоверность'''

    load_dotenv()  #Используется, чтобы из .env можно было подгрузить данные о лимитах
    time_check(report)
    distance_check(report)

