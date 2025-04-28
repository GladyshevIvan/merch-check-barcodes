from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Shops, UsedChecks


class SqlAlchemyCheckReviewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_shop_cords(self, shop_id, fn) -> Shops | None:
        '''Поиск по shop_id и fn координат магазина'''

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