from unittest import mock

import cloudinary
from django.core.files.base import ContentFile
from django.test import SimpleTestCase

from incidents.storage import CloudinaryStorage


class CloudinaryStorageTests(SimpleTestCase):
    def setUp(self):
        cloudinary.config(cloud_name='demo', api_key='key', api_secret='secret')
        self.storage = CloudinaryStorage()

    def test_save_uploads_and_returns_the_stored_name(self):
        reply = {'public_id': 'incidents/5/abc', 'format': 'jpg'}
        with mock.patch('cloudinary.uploader.upload', return_value=reply) as upload:
            name = self.storage.save('incidents/5/abc.jpg', ContentFile(b'data'))
        self.assertEqual(name, 'incidents/5/abc.jpg')
        self.assertEqual(upload.call_args.kwargs['public_id'], 'incidents/5/abc')
        self.assertEqual(upload.call_args.kwargs['resource_type'], 'image')

    def test_the_url_points_at_cloudinary_over_https(self):
        url = self.storage.url('incidents/5/abc.jpg')
        self.assertTrue(url.startswith('https://res.cloudinary.com/demo/image/upload/'))
        self.assertTrue(url.endswith('incidents/5/abc.jpg'))

    def test_names_never_collide_so_exists_is_false(self):
        self.assertFalse(self.storage.exists('incidents/5/abc.jpg'))

    def test_delete_removes_the_remote_file(self):
        with mock.patch('cloudinary.uploader.destroy') as destroy:
            self.storage.delete('incidents/5/abc.jpg')
        destroy.assert_called_once_with('incidents/5/abc', resource_type='image')