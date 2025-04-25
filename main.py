from fastapi import FastAPI, File, UploadFile, Body
from uuid import UUID
from app.core.convertations import convert_str_to_datetime, convert_str_to_tuple
from app.models.validation_models import Report
from app.core.barcode_recognizer import barcode_handler
from app.core.data_check import is_a_check_valid


app = FastAPI()


@app.post('/send_report')
async def march_check(
                      barcode_img: UploadFile = File(...),
                      date_and_time: str = Body(...),
                      gps_cords: str = Body(),
                      employee_id: UUID = Body(...),
                      shop_id: UUID = Body(...)
                      ):

    #Извлечение информации из штрихкода и возврат в виде словаря
    barcode_data = await barcode_handler(barcode_img)

    #Преобразование date_and_time в правильный вид
    formatted_date_string = convert_str_to_datetime(date_and_time)

    #Преобразование gps_cords в Tuple[float, float]
    gps_tuple = convert_str_to_tuple(gps_cords)

    try:
        #Получение провалидированного объекта Pydantic модели Report
        report = Report(
            date_and_time = formatted_date_string,
            gps = gps_tuple,
            employee_id = employee_id,
            shop_id = shop_id,
            t = convert_str_to_datetime(barcode_data['t']),
            s = barcode_data['s'],
            fn = barcode_data['fn'],
            i = barcode_data['i'],
            fp = barcode_data['fp'],
            n = barcode_data['n'],
        )

        #Проверка на подделку и актуальность
        try:
            is_a_check_valid(report)
            return 'Принято'
        except Exception as err:
            return f'Не принято {err}'

    except Exception:
        return 'Ошибка при распознании или данные некорректны'