from numpy import frombuffer, uint8
import cv2
import zxingcpp
from app.core.convertations import convert_string_to_dict


ALLOWED_IMG_TYPES = ('image/png', 'image/jpg', 'image/jpeg', 'image/webp')


async def detect_and_decode_barcode(image):
    '''Определяет наличие штрихкода на изображении и извлекает из него информацию

    Принимает изображение в виде строки - пути к файлу или байтового объекта,
    обрабатывает его и пытается обнаружить штрихкод. Если штрихкод найден,
    возвращает его данные и тип.

    Args:
        image (str или bytes): изображение

    Returns:
        list из двух элементов:
            - barcode_text (str): данные из штрихкода
            - barcode_format (str): тип штрихкода
        или
        None: если штрихкод не обнаружен
    '''

    #Проверка является ли файл изображением:
    if image.content_type not in ALLOWED_IMG_TYPES:
        raise Exception('Wrong type')

    #Преобразование UploadFiles в bytes
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


async def barcode_handler(image):

    #Извлечение информации из штрихкода
    barcode_data_string = await detect_and_decode_barcode(image)

    #Возвращение словаря из информации о штрихкоде
    return convert_string_to_dict(barcode_data_string)