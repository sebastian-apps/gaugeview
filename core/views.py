from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.http import JsonResponse
from .models import Camera, Image
from django.db.models import Count, Sum, Max
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CameraSerializer, ImageSerializer
from rest_framework import generics
from rest_framework.exceptions import NotFound
from operator import itemgetter

NOT_FOUND = {"Not Found" : "choose metric: num_images, total_sizes, or largest_file_sizes"}



def index(request):
    return render(request, 'core/index.html')



class CameraList(APIView):
    """ Request all cameras """
    def get(self, request):
        cameras = Camera.objects.all()
        data = CameraSerializer(cameras, many=True).data
        return Response(data)



class CameraSpecific(APIView):
    """ Request individual camera based on its camera_id """
    def get(self, request, pk):
        camera = get_object_or_404(Camera, pk=pk)
        data = CameraSerializer(camera).data
        return Response(data)




class CameraQuery(generics.ListCreateAPIView):
    """
    Query the cameras and order according to some params:

    /camera/order?num_images=1 returns the camera with the most images
    /camera/order?num_images=2 returns the top two cameras with the most images
    /camera/order?total_sizes=1 returns the camera with the most data
    /camera/order?largest_file_sizes=1 returns the camera with the largest image file size
    """
    model = Camera
    serializer_class = CameraSerializer

    def get_queryset(self):
        queryset = None
        num_images = self.request.query_params.get('num_images')
        total_size = self.request.query_params.get('total_sizes')
        largest_file_size = self.request.query_params.get('largest_file_sizes')

        if num_images:
            queryset = Camera.objects.annotate(count=Count('images')).order_by('-count')[:int(num_images)]

        elif total_size:
            queryset = Camera.objects.annotate(total_size=Sum('images__file_size')).order_by('-total_size')[:int(total_size)]

        elif largest_file_size:
            queryset = Camera.objects.annotate(maximum=Max('images__file_size')).order_by('-maximum')[:int(largest_file_size)]

        else:
            raise NotFound(NOT_FOUND)

        return queryset




class CameraFind(APIView):
    """
    Obtain aggregate information.

    /camera/find/num_images/
    /camera/find/total_sizes/
    /camera/find/largest_file_sizes/
    """
    def get(self, request, metric):


        if metric == "num_images":
            """
                Find the cameras with the most images. Sort from highest to lowest.
            """
            camera_list = []
            cameras = Camera.objects.all()
            for camera in cameras:
                num_images = Image.objects.filter(camera=camera).aggregate(count=Count('file_size'))
                camera_list.append({"camera_id": camera.camera_id, "num_images" : num_images.get("count")})
            response = {"cameras_num_images" : sorted(camera_list, key = lambda i: i['num_images'], reverse=True)}



        elif metric == "total_sizes":
            """
                Find the cameras with the most data. Sort from largest to smallest.
            """
            camera_list = []
            cameras = Camera.objects.all()
            for camera in cameras:
                total_size = Image.objects.filter(camera=camera).aggregate(total_size=Sum('file_size'))
                if total_size.get("total_size") is not None: # Excludes cameras that have no images.
                    camera_list.append({"camera_id": camera.camera_id, "total_size" : total_size.get("total_size")})
            response = {"cameras_total_sizes": sorted(camera_list, key = lambda i: i['total_size'], reverse=True)}



        elif metric == "largest_file_sizes":
            """
                Find the largest file of each camera. Sort from largest to smallest.
            """
            camera_list = []
            cameras = Camera.objects.all()
            for camera in cameras:
                largest_file_size = Image.objects.filter(camera=camera).aggregate(largest_file_size=Max('file_size'))
                if largest_file_size.get("largest_file_size") is not None:  # Excludes cameras that have no images.
                    camera_list.append({"camera_id": camera.camera_id, "largest_file_size": largest_file_size.get("largest_file_size")})
            response = {"cameras_largest_file_sizes" : sorted(camera_list, key = lambda i: i['largest_file_size'], reverse=True)}

        else:
            raise NotFound(NOT_FOUND)

        return Response(response)
