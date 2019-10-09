from django.test import SimpleTestCase
from django.urls import reverse, resolve
from core.views import CameraList, CameraSpecific, CameraQuery, CameraFind

class TestUrls(SimpleTestCase):

    def test_camera_list_resolves(self):
        url = reverse('core:camera_list')
        self.assertEquals(resolve(url).func.view_class, CameraList)

    def test_camera_specific_resolves(self):
         url = reverse('core:camera_specific', args=[1])
         self.assertEquals(resolve(url).func.view_class, CameraSpecific)

    def test_camera_query_resolves(self):
        url = reverse('core:camera_query')
        self.assertEquals(resolve(url).func.view_class, CameraQuery)

    def test_camera_find_resolves(self):
        url = reverse('core:camera_find', args=["num_images"])
        self.assertEquals(resolve(url).func.view_class, CameraFind)
