import os

import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from django.core.files.storage import Storage


class CloudinaryStorage(Storage):
    """Store uploaded images on Cloudinary (a server's own disk does not survive a restart)."""

    @staticmethod
    def _split(name):
        public_id, extension = os.path.splitext(name)
        return public_id, extension.lstrip('.')

    def _save(self, name, content):
        public_id, _ = self._split(name)
        content.seek(0)
        result = cloudinary.uploader.upload(
            content, public_id=public_id, resource_type='image', overwrite=False
        )
        return f"{result['public_id']}.{result['format']}"

    def exists(self, name):
        return False   # names are random uuids, so two uploads never collide

    def url(self, name):
        public_id, extension = self._split(name)
        return cloudinary_url(public_id, format=extension, secure=True)[0]

    def delete(self, name):
        public_id, _ = self._split(name)
        cloudinary.uploader.destroy(public_id, resource_type='image')