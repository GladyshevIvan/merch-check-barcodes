from fastapi import FastAPI, File, UploadFile, Body, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.convertations import convert_str_to_datetime
from app.core.data_check import BarcodeDataCheck
from app.db.database import get_async_session
from app.repositories.check_review_repository import SqlAlchemyCheckReviewRepository


app = FastAPI()


@app.post('/send_report')
async def merch_check(
                      barcode_img: UploadFile = File(...),
                      date_and_time: str = Body(...),
                      latitude: float = Body(...),
                      longitude: float = Body(...),
                      employee_id: UUID = Body(...),
                      shop_id: UUID = Body(...),
                      session: AsyncSession = Depends(get_async_session) #Зависимость для получения асинхронной сессии, чтобы взаимодействовать с Базой Данных
                      ):
    '''
    Срабатывает для конечной точки "/send_report", принимает параметры и после предварительной обработки - переработки даты из строки в нужный формат,
    Создает класс и вызывает метод для проверки, куда передаются параметры
    Возвращает, что, либо штрихкод принят, либо - нет
    '''

    #Преобразование date_and_time в правильный вид
    formatted_date_string = convert_str_to_datetime(date_and_time)

    #Создание объекта репозитория, который через сессию будет работать с Базой Данных
    repository = SqlAlchemyCheckReviewRepository(session)

    #Класс для проверки штрихода на соответствие условиям, куда передается объект репозитория для доступа к Базе Данных
    validation_obj = BarcodeDataCheck(repository)

    #Вызов метода, который проверяет штрихкод на соответствие
    return await validation_obj.review(
        barcode_img = barcode_img,
        date_and_time = formatted_date_string,
        gps = (latitude, longitude),
        employee_id = employee_id,
        shop_id = shop_id
    )