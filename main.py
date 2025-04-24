from fastapi import FastAPI, File, UploadFile, Body
from app.models.validation_models import Report
from app.barcode_handler.barcode_recognizer import detect_and_decode_barcode


app = FastAPI()


@app.post('/send_report')
async def march_check(barcode_img: UploadFile = File(...)):

    #Извлечение информации из штрихкода
    return await detect_and_decode_barcode(barcode_img)



# @app.post('/send_report')
# async def march_check(barcode_img: UploadFile = File(...), report: Report = Body(...)):
#
#     #Извлечение информации из штрихкода
#     barcode_data = detect_and_decode_barcode(barcode_img)