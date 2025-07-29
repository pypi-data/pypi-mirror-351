from django.test import TestCase, override_settings
from vendor_images.models import VendorImage
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
import shutil
from django.contrib.auth.models import User
from django.conf import settings
import os
from io import BytesIO
from PIL import Image


TEMP_MEDIA_ROOT = tempfile.mkdtemp()

def get_test_image_file():
    img = Image.new('RGB', (100, 100), color='red')
    byte_io = BytesIO()
    img.save(byte_io, 'JPEG')
    byte_io.seek(0)
    return SimpleUploadedFile('test.jpg', byte_io.read(), content_type='image/jpeg')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class VendorImageModelTest(TestCase):
    def setUp(self):
        self.vendor = User.objects.create_user(username='vendor1', password='12345')
        self.image_file = get_test_image_file()

    def test_create_vendor_image_with_vendor_instance(self):
        image = VendorImage.objects.create(
            vendor=self.vendor,
            image=self.image_file,
            image_type='logo'
        )
        image.refresh_from_db()
        print("image_url:", image.image_url)
        self.assertTrue(image.image_url.startswith("/media/"))

    def test_create_vendor_image(self):
        image = VendorImage.objects.create(
            vendor=self.vendor,
            image=self.image_file,
            image_type='logo'
        )
        image.refresh_from_db()
        self.assertTrue(image.image_url.startswith('/media/'))

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
