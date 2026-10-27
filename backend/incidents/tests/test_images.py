import io
import os
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image

from .base import ApiTestCase


def photo(name='p.jpg'):
    buffer = io.BytesIO()
    Image.new('RGB', (20, 20), 'red').save(buffer, 'JPEG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/jpeg')


class ImageTests(ApiTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        tmp = tempfile.mkdtemp()                       # uploads go to a throw-away folder
        cls.addClassCleanup(shutil.rmtree, tmp, True)
        override = override_settings(MEDIA_ROOT=tmp)
        override.enable()
        cls.addClassCleanup(override.disable)

    def setUp(self):
        super().setUp()
        self.inc = self.make()
        self.url = f'/api/incidents/{self.inc.id}/images/'

    def upload(self, user, file=None):
        self.login(user)
        return self.client.post(self.url, {'image': file or photo()}, format='multipart')

    def test_the_reporter_uploads_a_photo(self):
        res = self.upload(self.citizen)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(len(res.data['images']), 1)
        self.assertIn('/media/incidents/', res.data['images'][0]['image'])

    def test_a_text_file_renamed_jpg_is_rejected(self):
        fake = SimpleUploadedFile('fake.jpg', b'this is not an image', content_type='image/jpeg')
        self.assertEqual(self.upload(self.citizen, fake).status_code, 400)

    def test_a_photo_over_5_mb_is_rejected(self):
        big = io.BytesIO()
        Image.frombytes('RGB', (1500, 1500), os.urandom(1500 * 1500 * 3)).save(big, 'BMP')  # about 6.7 MB
        file = SimpleUploadedFile('big.bmp', big.getvalue(), content_type='image/bmp')
        self.assertEqual(self.upload(self.citizen, file).status_code, 400)

    def test_at_most_three_photos(self):
        for _ in range(3):
            self.assertEqual(self.upload(self.citizen).status_code, 201)
        self.assertEqual(self.upload(self.citizen).status_code, 400)

    def test_a_stranger_cannot_upload(self):
        self.assertEqual(self.upload(self.citizen2).status_code, 404)   # cannot even see it

    def test_no_photos_after_it_is_resolved(self):
        self.inc.status = 'resolved'
        self.inc.save()
        self.assertEqual(self.upload(self.citizen).status_code, 400)

    def test_anonymous_gets_401(self):
        self.assertEqual(self.client.post(self.url, {'image': photo()}, format='multipart').status_code, 401)