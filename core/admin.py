from django.contrib import admin

# Register your models here.

from core.models import Camera, Image

admin.site.register(Camera)
admin.site.register(Image)
