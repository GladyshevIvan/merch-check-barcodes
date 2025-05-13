from numpy import frombuffer, uint8
from typing import List
from fastapi import UploadFile
import cv2
import zxingcpp
from app.core.convertations import convert_string_to_dict


ALLOWED_IMG_TYPES = ('image/png', 'image/jpg', 'image/jpeg', 'image/webp') #Разрешенные типы файлов


async def detect_and_decode_barcode(image: UploadFile) -> List | None:
    '''
    Функция, распознающая штрихкоды на изображениях

    Определяет наличие штрихкода на изображении и извлекает из него информацию.
    Принимает изображение в виде строки - пути к файлу или байтового объекта,
    обрабатывает его и пытается обнаружить штрихкод. Если штрихкод найден,
    возвращает его данные и тип

    Args:
        image (UploadFiles): Файл изображения
    Returns:
        str: Строка с содержимым штрихкода типа 't=20180412T102900&s=1800.00&fn=9999078900004658&i=171&fp=2256047510&n=1'
            или
        None: если штрихкод не обнаружен
    Raises:
        Exception: Если расширение файла не входит в ALLOWED_IMG_TYPES
    '''

    #Проверка является ли файл изображением:
    if image.content_type not in ALLOWED_IMG_TYPES:
        raise Exception('Неправильный тип')

    #Преобразование UploadFiles в bytes (Проверить тип: I/O или CPU и принять решение о целесообразности асинхрона)
    image = await image.read()

    #Преобразование bytes в cv2.typing.MatLike
    nparr = frombuffer(image, uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    barcodes = zxingcpp.read_barcodes(img) #Распознание штрихкодов

    #Проверка распознал ли zxing штрихкоды
    if barcodes:
        #Если на изображении есть штрихкоды, а их может быть и несколько возвращается информация из самого первого
        return barcodes[0].text

    return None


async def barcode_handler(image: UploadFile) -> dict:
    '''
    Обработчик для распознавания и обработки штрихкодов из изображений

    Извлекает данные штрихкода из переданного изображения в виде строки и затем преобразует
    их в словарь

    Args:
        image (UploadFile): Файл изображения
    Returns:
        dict: Словарь, содержащий данные штрихкода
    Raises:
        Exception: Если на изображении нет штрихкода или его не удалось распознать
    '''

    #Извлечение информации из штрихкода
    barcode_data_string = await detect_and_decode_barcode(image)

    #Возвращение словаря из информации о штрихкоде
    return convert_string_to_dict(barcode_data_string)