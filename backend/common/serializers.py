# common/serializers.py
import base64
import uuid

from django.core.files.base import ContentFile  # type: ignore
from rest_framework import serializers  # type: ignore


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format_, imgstr = data.split(';base64,')
            ext = format_.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr),
                name=f'{uuid.uuid4()}.{ext}',
            )
        return super().to_internal_value(data)
