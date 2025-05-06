from datetime import datetime
from uuid import UUID
import pytest
import pytz
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
    MOCK_SHOP =(
        MockShopsModel(
            shop_id=UUID('F10F6CAF-5A98-426C-80D5-281A5D6FF0B3'),
            fn='9999078900004658',
            latitude=64.527603,
            longitude=40.574157
        ),
    )

    #Псевдотаблица UsedChecks из Базы Данных
    MOCK_USED_CHECKS = (
        MockUsedChecksModel(
            t=pytz.utc.localize(datetime(2025, 4, 23, 20, 12, 2)),
            i=100,
            fn='1999078900004658',
            fp=2256047511
        ),
    )

    async def get_shop_cords(self, shop_id, fn):
        '''Метод, который подменит get_shop_cords в SqlAlchemyCheckReviewRepository'''

        for item in self.MOCK_SHOP:
            if item.shop_id == shop_id and item.fn == fn:
                return item

    async def get_fp_fn(self, fp, fn):
        '''Метод, который подменит get_fp_fn в SqlAlchemyCheckReviewRepository'''

        for item in self.MOCK_USED_CHECKS:
            if item.fp == fp and item.fn == fn:
                return item

    async def get_t_fn_i(self, t, fn, i):
        '''Метод, который подменит get_t_fn_i в SqlAlchemyCheckReviewRepository'''

        for item in self.MOCK_USED_CHECKS:
            if item.t == t and item.fn == fn and item.i == i:
                return item


#Псевдообъекты класса Report для теста distance_check
@pytest.mark.asyncio
@pytest.mark.parametrize(
    'report, expected_result',
    [
        (
            MockReport(
                gps=(64.527603, 40.574157),
                shop_id=UUID('F10F6CAF-5A98-426C-80D5-281A5D6FF0B3'),
                fn='9999078900004658'),
            True
        ),
        (
            MockReport(
                gps=(84.527603, 40.574157),
                shop_id=UUID('F10F6CAF-5A98-426C-80D5-281A5D6FF0B3'),
                fn='9999078900004658'),
            pytest.raises(Exception)
        ),
        (
            MockReport(
                gps=(84.527603, 40.574157),
                shop_id=UUID('F10F6CAF-5A98-426C-80D5-281A5D6FF0B9'),
                fn='9999078900004658'
            ),
            pytest.raises(Exception)
        )
    ],
)
async def test_distance_check(mocker, report, expected_result):
    '''Проврка на дистанцию с мокированием Базы Данных с использованием фикстуры mocker для подмены метода на мокированный'''

    #Создание экземпляра мокового репозитория
    mock_repo = MockSqlAlchemyCheckReviewRepository()

    #Мокирование метода get_shop_cords из SqlAlchemyCheckReviewRepository на методы MockSqlAlchemyCheckReviewRepository
    mocker.patch('app.repositories.check_review_repository.SqlAlchemyCheckReviewRepository.get_shop_cords', new=mock_repo.get_shop_cords)

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
        (
            MockReport(
                t=pytz.utc.localize(datetime(2025, 4, 23, 20, 12, 2)),
                i=171,
                fn='9999078900004658',
                fp=2256047510
            ),
            True
        ),
        (
            MockReport(
                t=pytz.utc.localize(datetime(2025, 4, 23, 20, 12, 2)),
                i=100,
                fn='1999078900004658',
                fp=2256047510
            ),
            pytest.raises(Exception)
        ),
        (
            MockReport(
                t=pytz.utc.localize(datetime(2024, 4, 23, 20, 12, 2)),
                i=101,
                fn='1999078900004658',
                fp=2256047511
            ),
            pytest.raises(Exception)
        )
    ],
)
async def test_check_dublicats(mocker, report, expected_result):
    '''Проврка на дубликаты с мокированием Базы Данных с использованием фикстуры mocker для подмены методов на мокированный'''

    #Создание экземпляра мокового репозитория
    mock_repo = MockSqlAlchemyCheckReviewRepository()

    #Мокирование методов get_fp_fn и get_t_fn_i из SqlAlchemyCheckReviewRepository на методы MockSqlAlchemyCheckReviewRepository
    mocker.patch('app.repositories.check_review_repository.SqlAlchemyCheckReviewRepository.get_fp_fn', new=mock_repo.get_fp_fn)
    mocker.patch('app.repositories.check_review_repository.SqlAlchemyCheckReviewRepository.get_t_fn_i', new=mock_repo.get_t_fn_i)

    if isinstance(expected_result, type(pytest.raises(Exception))):
        with expected_result:
            await BarcodeDataCheck.check_dublicats(report)
    else:
        result = await BarcodeDataCheck.check_dublicats(report)
        assert result == expected_result