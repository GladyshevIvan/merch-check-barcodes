import random
import mimetypes
from locust import HttpUser, task, between


IMAGES_FILES = ['tests/barcodes_imgs/barcode1.png']


class MerchTestUser(HttpUser):
    '''locust-класс, представляющий мерчендайзера, загружающего изображение'''

    #wait_time = between(0.5, 3.0)

    def on_start(self):
        pass


    def on_stop(self):
        pass


    @task(1)
    def post_request_user(self):
        image_file = random.choice(IMAGES_FILES)
        with open(image_file, 'rb') as f:
            content_type = mimetypes.guess_type(image_file)[0]
            files = {'barcode_img': (image_file, f, content_type)}
            data = {
                'date_and_time': '20180412T102900',
                'latitude': 64.527603,
                'longitude': 40.574157,
                'employee_id': 'F10F6CAF-5A98-426C-80D5-281A5D6FF0B8',
                'shop_id': 'F10F6CAF-5A98-426C-80D5-281A5D6FF0B3'
            }
            self.client.post(
                '/send_report',
                data=data,
                files=files
            )