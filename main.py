from fastapi import FastAPI, File, UploadFile, Body
from uuid import UUID
from app.core.convertations import convert_str_to_datetime
from app.core.data_check import BarcodeDataCheck


app = FastAPI()


@app.post('/send_report')
async def march_check(
                      barcode_img: UploadFile = File(...),
                      date_and_time: str = Body(...),
                      latitude: float = Body(...),
                      longitude: float = Body(...),
                      employee_id: UUID = Body(...),
                      shop_id: UUID = Body(...)
                      ):
    '''
    Срабатывает для конечной точки "/send_report", принимает параметры и после предварительной обработки - переработки даты из строки в нужный формат,
    Создает класс и вызывает метод для проверки, куда передаются параметры
    Возвращает, что, либо штрихкод принят, либо - нет
    '''

    #Преобразование date_and_time в правильный вид
    formatted_date_string = convert_str_to_datetime(date_and_time)

    #Класс для проверки штрихода на соответствие условиям
    validation_obj = BarcodeDataCheck()

    #Вызов метода, который проверяет штрихкод на соответствие
    return await validation_obj.review(
        barcode_img = barcode_img,
        date_and_time = formatted_date_string,
        gps = (latitude, longitude),
        employee_id = employee_id,
        shop_id = shop_id
    )