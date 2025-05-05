import pickle
from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Shops, UsedChecks
from app.config import create_redis_client


def redis_wrapper(func):
    '''Асинхронный декоратор для '''

    @wraps(func)
    async def wrapper(*args, **kwargs):
        redis_client = None  #Инициализирование redis_client, чтобы его было удобнее закрыть через finally

        try:
            redis_client = await create_redis_client()
            cache_key = f'{func.__name__}: kwargs:{kwargs}' #Ключ для Redis
            cached_result = await redis_client.get(cache_key) #Получение по ключу данных из Redis

            if cached_result:
                #Использование закэшированного результата
                return pickle.loads(cached_result)
            else:
                #Получение результата из функции и его кеширование в Redis
                result = await func(*args, **kwargs)
                await redis_client.setex(cache_key, 3600, pickle.dumps(result))
                return result

        except Exception as err:
            raise Exception(f'Ошибка при работе с Redis {err}')
        finally:
            if redis_client:
                await redis_client.close()

    return wrapper


class SqlAlchemyCheckReviewRepository:
    '''Репозиторий для выполнения запросов, связанных с проверкой чеков, к Базе Данных'''

    def __init__(self, session: AsyncSession):
        self.session = session #Асинхронная сессия, через которую происходит взаимодействие с Базой Данных


    @redis_wrapper
    async def get_shop_cords(self, shop_id, fn) -> Shops | None:
        '''Поиск по shop_id и fn координат магазина, используется кеширование Redis через декоратор'''

        result = await self.session.execute(select(Shops).filter_by(shop_id=shop_id, fn=fn))
        return result.scalars().first()


    async def get_fp_fn(self, fp, fn) -> UsedChecks | None:
        '''Проверка есть ли в Базе Данных чек с такими же "fp", "fn"'''

        result = await self.session.execute(select(UsedChecks).filter_by(fp=fp, fn=fn))
        return result.scalars().first()


    async def get_t_fn_i(self, t, fn, i) -> UsedChecks | None:
        '''Проверка есть ли в Базе Данных чек с такими же "t", "fn" и "i"'''

        result = await self.session.execute(select(UsedChecks).filter_by(t=t, fn=fn, i=i))
        return result.scalars().first()


    async def add_used_check(self, fp, fn, t, i):
        '''Добавление прошедшего проверку чека в Базу Данных'''

        new_check = UsedChecks(fp=fp, fn=fn, t=t, i=i)
        self.session.add(new_check)
        await self.session.commit()