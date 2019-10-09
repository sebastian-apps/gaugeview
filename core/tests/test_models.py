from django.test import TestCase
from core.models import Camera, Image
from django.urls import reverse
import random
import requests

N_CAMERAS = 100
M_FILES = 100
TIMEOUT = 1
LOCALHOST = "http://localhost:8000/"


class CameraTestCase(TestCase):

    @classmethod
    def setUpTestData(self):
        """
            Set up four cameras to start.
            Camera 1 (i.e., camera_id: 1) has the most image files.
            Camera 3 has used the most data and has the largest file.
            Camera 4 has no images.
        """
        camera_1 = Camera.objects.create(camera_id=1)
        Image.objects.create(camera=camera_1, file_size=51200)
        Image.objects.create(camera=camera_1, file_size=1024)
        Image.objects.create(camera=camera_1, file_size=3072)

        camera_2 = Camera.objects.create(camera_id=2)
        Image.objects.create(camera=camera_2, file_size=1024)
        Image.objects.create(camera=camera_2, file_size=1024)

        camera_3 = Camera.objects.create(camera_id=3)
        Image.objects.create(camera=camera_3, file_size=921600)

        Camera.objects.create(camera_id=4)


    def setUp(self):
        pass


    def test_num_images(self):
        """
            Camera 1 should have the most image files.
        """
        url = reverse('core:camera_find', args=["num_images"])
        response = self.client.get(url)
        top_camera_id = list(response.data.get("cameras_num_images"))[0].get("camera_id")
        self.assertEqual(top_camera_id, 1)



    def test_total_sizes(self):
        """
            This Camera 3 should have the greatest sum of file sizes.
        """
        url = reverse('core:camera_find', args=["total_sizes"])
        response = self.client.get(url)
        top_camera_id = list(response.data.get("cameras_total_sizes"))[0].get("camera_id")
        self.assertEqual(top_camera_id, 3)



    def test_largest_file_sizes(self):
        """
            Camera 3 should have the file with the largest size.
        """
        url = reverse('core:camera_find', args=["largest_file_sizes"])
        response = self.client.get(url)
        top_camera_id = list(response.data.get("cameras_largest_file_sizes"))[0].get("camera_id")
        self.assertEqual(top_camera_id, 3)



    def test_camera_specific(self):
        """
            Create N_CAMERAS number of cameras, each with M_FILES number of files.
            Request each camera's details individually. Should get 200 status code.
            Also, request camera with camera_id: N_CAMERAS + 1. Should return 404.
        """
        for i in range(5, N_CAMERAS):  # Start at 5 because 4 cameras have already been created.
            cam = Camera.objects.create(camera_id=i)
            for j in range(M_FILES):
              Image.objects.create(camera=cam, file_size=random.randint(1,5001)*1024)  # Random for no particular reason

        cameras = Camera.objects.all()
        for camera in cameras:
            url = reverse('core:camera_specific', args=[camera.camera_id])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        """ This camera should not exist. """
        url = reverse('core:camera_specific', args=[N_CAMERAS + 1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)




    def test_camera_list(self):
        """
            Request all cameras simultaneously. Should get 200 status code.
        """
        for i in range(5, N_CAMERAS):  # Start at 5 because 4 cameras have already been created.
            cam = Camera.objects.create(camera_id=i)
            for j in range(M_FILES):
              Image.objects.create(camera=cam, file_size=random.randint(1,5001)*1024)

        url = reverse('core:camera_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), N_CAMERAS-1)



    def test_camera_list_with_timeout(self):
        """
            Test request timeout.
        """
        for i in range(5, N_CAMERAS):  # Start at 5 because 4 cameras have already been created.
            cam = Camera.objects.create(camera_id=i)
            for j in range(M_FILES):
              Image.objects.create(camera=cam, file_size=random.randint(1,5001)*1024)

        url = LOCALHOST + "camera/"
        response = requests.get(url, timeout=TIMEOUT)
        self.assertEqual(response.status_code, 200)
