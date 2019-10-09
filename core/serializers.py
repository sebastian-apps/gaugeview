from rest_framework import serializers, fields
from .models import Camera, Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('file_size',)


class CameraSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True, required=False)
    class Meta:
        model = Camera
        fields = ('camera_id', "images")
