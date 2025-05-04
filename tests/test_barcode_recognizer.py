import os
from io import BytesIO
import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers
import mimetypes
from app.core.barcode_recognizer import detect_and_decode_barcode


#Файлы, которые будут использоваться для тестирования и ожидаемые результаты
test_files = [
    ('tests/barcodes_imgs/barcode1.png', 't=20180412T102900&s=1800.00&fn=9999078900004658&i=171&fp=2256047510&n=1'),
    ('tests/barcodes_imgs/barcode1.jpg', 't=20180412T102900&s=1800.00&fn=9999078900004658&i=171&fp=2256047510&n=1'),
    ('tests/barcodes_imgs/barcode1.jpeg', 't=20180412T102900&s=1800.00&fn=9999078900004658&i=171&fp=2256047510&n=1'),
    ('tests/barcodes_imgs/barcode1.webp', 't=20180412T102900&s=1800.00&fn=9999078900004658&i=171&fp=2256047510&n=1'),
    ('tests/barcodes_imgs/img_without_barcode.png', None),
    ('tests/barcodes_imgs/img_without_barcode.jpg', None),
    ('tests/barcodes_imgs/img_without_barcode.jpeg', None),
    ('tests/barcodes_imgs/img_without_barcode.webp', None),
    ('tests/barcodes_imgs/wrong_type_file.txt', pytest.raises(Exception)),
    ('', pytest.raises(Exception))
]


@pytest.mark.parametrize(
    'image_path, expected_result',
    test_files
)
async def test_detect_and_decode_barcode(image_path, expected_result):
    '''Проврка распознания штрихкодов'''

    if image_path:
        with open(image_path, 'rb') as f:
            image_data = f.read()

            #Определение content-type файла
            content_type = mimetypes.guess_type(image_path)[0]
            if content_type is None:
                content_type = 'application/octet-stream'
    else:
        image_data = None
        content_type = 'application/octet-stream'

    #Создание заголовка с 'content-type', потому что напрямую передать 'content-type' в UploadFiles - нельзя
    headers = Headers({'content-type': content_type})

    #Создание UploadFile из байтовых данных
    image_file = UploadFile(filename=os.path.basename(image_path), file=BytesIO(image_data), headers=headers)

    if isinstance(expected_result, type(pytest.raises(Exception))):
        with expected_result:
            await detect_and_decode_barcode(image_file)
    else:
        result = await detect_and_decode_barcode(image_file)
        assert result == expected_result