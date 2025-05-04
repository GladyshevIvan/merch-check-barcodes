from datetime import datetime
from uuid import UUID
import pytest
import pytz
from unittest.mock import patch
from app.config import settings
from app.core.data_check import BarcodeDataCheck


class MockReport:
    '''Псевдокласс, имитирующий Report'''

    def __init__(self, t=None, date_and_time=None, gps=None, employee_id=None, shop_id=None, s=None, fn=None, i=None, fp=None, n=None):
        self.t = t
        self.date_and_time = date_and_time
        self.gps = gps
        self.employee_id = employee_id
        self.shop_id = shop_id
        self.s = s
        self.fn = fn
        self.i = i
        self.fp = fp
        self.n = n


#Параметры для проверки функции time_check
@pytest.mark.parametrize(
    'report, expected_result',
    [
        (
            MockReport(
                t=pytz.utc.localize(datetime(2025, 4, 23, 20, 12, 2)),
                date_and_time=pytz.utc.localize(datetime(2025, 4, 23, 20, 12, 2))),
                True
        ),
        (
            MockReport(
                t=pytz.utc.localize(datetime(2025, 4, 23, 20, 12, 2)),
                date_and_time=pytz.utc.localize(datetime(2025, 4, 23, 22, 12, 2))),
                True
        ),
        (
            MockReport(
                t=pytz.utc.localize(datetime(2025, 4, 23, 20, 12, 2)),
                date_and_time=pytz.utc.localize(datetime(2025, 4, 23, 22, 13, 2))),
                pytest.raises(Exception)
        ),
        (
            MockReport(
                t=pytz.timezone(settings.TIME_ZONE).localize(datetime(2025, 4, 23, 20, 12, 2)),
                date_and_time=pytz.timezone(settings.TIME_ZONE).localize(datetime(2025, 4, 23, 20, 12, 2))),
                True
        ),
        (
            MockReport(
                t=pytz.timezone(settings.TIME_ZONE).localize(datetime(2025, 4, 23, 20, 12, 2)),
                date_and_time=pytz.timezone(settings.TIME_ZONE).localize(datetime(2025, 4, 23, 22, 12, 2))),
                True
        ),
        (
            MockReport(
                t=pytz.timezone(settings.TIME_ZONE).localize(datetime(2025, 4, 23, 20, 12, 2)),
                date_and_time=pytz.timezone(settings.TIME_ZONE).localize(datetime(2025, 4, 23, 22, 12, 3))),
                pytest.raises(Exception)
        ),
    ]
)


def test_time_check(report, expected_result):
    '''Проверка на время'''

    if isinstance(expected_result, type(pytest.raises(ValueError))):
        with expected_result:
            BarcodeDataCheck.time_check(report)
    else:
        result = BarcodeDataCheck.time_check(report)
        assert result == expected_result


class MockShopsModel:
    '''Псевдомодель Shops'''

    def __init__(self, shop_id, fn, latitude, longitude):
        self.shop_id = shop_id
        self.fn = fn
        self.latitude = latitude
        self.longitude = longitude


class MockUsedChecksModel:
    '''Псевдомодель UsedCheck'''

    def __init__(self, fp, fn, i, t):
        self.fp = fp
        self.fn = fn
        self.i = i
        self.t = t


class MockSqlAlchemyCheckReviewRepository:
    '''Псевдорепозиторий SqlAlchemyCheckReviewRepository'''

    #Псевдотаблица Shops из Базы Данных
    MOCK_SHOP = (
        MockShopsModel(shop_id=UUID('F10F6CAF-5A98-426C-80D5-281A5D6FF0B3'), fn='9999078900004658', latitude=64.527603, longitude=40.574157),
    )

    #Псевдотаблица UsedChecks из Базы Данных
    MOCK_USED_CHECKS = (
        MockUsedChecksModel(t=pytz.utc.localize(datetime(2025, 4, 23, 20, 12, 2)), i=100, fn='1999078900004658', fp=2256047510)
    )

    async def mock_get_shop_cords(self, shop_id, fn):
        '''Метод, который подменит get_shop_cords в SqlAlchemyCheckReviewRepository'''

        for item in self.MOCK_SHOP:
            if item.shop_id == shop_id and item.fn == fn:
                return item

    async def mock_get_fp_fn(self, fp, fn):
        '''Метод, который подменит get_fp_fn в SqlAlchemyCheckReviewRepository'''

        for item in self.MOCK_USED_CHECKS:
            if item.fp == fp and item.fn == fn:
                return item

    async def mock_get_t_fn_i(self, t, fn, i):
        '''Метод, который подменит get_t_fn_i в SqlAlchemyCheckReviewRepository'''

        for item in self.MOCK_USED_CHECKS:
            if item.t == t and item.fn == fn and item.i == i:
                return item


#Псевдообъекты класса Report для теста distance_check
@pytest.mark.asyncio
@pytest.mark.parametrize(
    'report, expected_result',
    [
        (MockReport(gps=(64.527603, 40.574157), shop_id=UUID('F10F6CAF-5A98-426C-80D5-281A5D6FF0B3'), fn='9999078900004658'), True),
        (MockReport(gps=(84.527603, 40.574157), shop_id=UUID('F10F6CAF-5A98-426C-80D5-281A5D6FF0B3'), fn='9999078900004658'), pytest.raises(Exception)),
        (MockReport(gps=(84.527603, 40.574157), shop_id=UUID('F10F6CAF-5A98-426C-80D5-281A5D6FF0B9'), fn='9999078900004658'), pytest.raises(Exception))
    ],
)


@patch('app.repositories.check_review_repository.SqlAlchemyCheckReviewRepository', new=MockSqlAlchemyCheckReviewRepository)
async def test_distance_check(report, expected_result):
    '''Проврка на дистанцию с мокированием Базы Данных'''

    if isinstance(expected_result, type(pytest.raises(ValueError))):
        with expected_result:
            await BarcodeDataCheck.distance_check(report)
    else:
        result = await BarcodeDataCheck.distance_check(report)
        assert result == expected_result


#Псевдообъекты класса Report для теста distance_check check_dublicats
@pytest.mark.asyncio
@pytest.mark.parametrize(
    'report, expected_result',
    [
        (MockReport(t=pytz.utc.localize(datetime(2025, 4, 23, 20, 12, 2)), i=171, fn='9999078900004658', fp=2256047510), True),
        (MockReport(t=pytz.utc.localize(datetime(2025, 4, 23, 20, 12, 2)), i=100, fn='1999078900004658', fp=2256047510), True)
    ],
)


@patch('app.repositories.check_review_repository.SqlAlchemyCheckReviewRepository', new=MockSqlAlchemyCheckReviewRepository)
async def test_check_dublicats(report, expected_result):
    '''Проврка на дубликаты с мокированием Базы Данных'''

    if isinstance(expected_result, type(pytest.raises(ValueError))):
        with expected_result:
            await BarcodeDataCheck.check_dublicats(report)
    else:
        result = await BarcodeDataCheck.check_dublicats(report)
        assert result == expected_result