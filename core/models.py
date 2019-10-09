from django.db import models

class Camera(models.Model):
    """ A Camera in the network """
    camera_id = models.IntegerField(primary_key=True)
    text = models.CharField(max_length = 280, null=True, blank=True, default=None)  # Extra field.
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.camera_id)



class Image(models.Model):
    """ Image from a Camera """
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='images')
    file_size = models.IntegerField()  # Here it's entered manually. Typically would be obtained directly from image.
    image_url = models.CharField(max_length = 600, null=True, blank=True, default=None) # Location of image file in cloud storage.
    text = models.CharField(max_length = 280, null=True, blank=True, default=None) # Extra field.
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Camera {}, {}, {}'.format(self.camera, self.file_size, self.date_added)
