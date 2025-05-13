from fastapi import FastAPI, File, UploadFile, Body, Depends
from uuid import UUID
from app.core.convertations import convert_str_to_datetime
from app.core.data_check import BarcodeDataCheck


app = FastAPI()


@app.post('/send_report')
async def merch_check(
                      barcode_img: UploadFile = File(...),
                      date_and_time: str = Body(...),
                      latitude: float = Body(...),
                      longitude: float = Body(...),
                      employee_id: UUID = Body(...),
                      shop_id: UUID = Body(...),
                      ) -> str:
    '''
    Эндпоинт для получения отчета от мерчендайзера

    Срабатывает для конечной точки '/send_report', принимает параметры
    и после предварительной обработки (переработки даты из строки в нужный формат)
    создает экземпляр класса BarcodeDataCheck и вызывает метод review для проверки, куда передаются параметры
    Возвращает, что, либо штрихкод принят, либо - нет

     Args:
        - barcode_img (UploadFile): Изображение штрихкода
        - date_and_time (str): Дата и время отчета в формате ISO 8601
        - latitude (float): Широта местоположения, откуда был отправлен отчет
        - longitude (float): Долгота местоположения, откуда был отправлен отчет
        - employee_id (UUID): UUID мерчендайзера, отправляющего отчет
        - shop_id (UUID): UUID магазина, в котором выполнил работу мерчендайзер
    Returns:
        str: Сообщение, 'Принят' или 'Не принят {описание ошибки}'
    '''

    #Преобразование date_and_time в правильный вид
    formatted_date_string = convert_str_to_datetime(date_and_time)

    #Класс для проверки штрихода на соответствие условиям, куда передается объект репозитория для доступа к Базе Данных
    validation_obj = BarcodeDataCheck()

    #Вызов метода, который проверяет штрихкод на соответствие
    return await validation_obj.review(
        barcode_img = barcode_img,
        date_and_time = formatted_date_string,
        gps = (latitude, longitude),
        employee_id = employee_id,
        shop_id = shop_id
    )