"""Defines URL patterns for core"""
from django.urls import path
from django.conf.urls import url, include
from . import views



app_name = 'core'

urlpatterns = [

    path('', views.index, name='index'),


    # Request all cameras
    path('camera/', views.CameraList.as_view(), name="camera_list"),


    # Request individual camera based on its camera_id (pk, primary key)
    path('camera/<int:pk>/', views.CameraSpecific.as_view(), name="camera_specific"),


    # Query the cameras and order according to some params:
    #
    # /camera/order?num_images=1 returns the camera with the most images
    # /camera/order?num_images=2 returns the top two cameras with the most images
    # /camera/order?total_sizes=1 returns the camera with the most data
    # /camera/order?largest_file_sizes=1 returns the camera with the largest image file size
    path('camera/order', views.CameraQuery.as_view(), name='camera_query'),


    # Obtain aggregate information.
    #
    # /camera/find/num_images/
    # /camera/find/total_sizes/
    # /camera/find/largest_file_sizes/
    path('camera/find/<str:metric>/', views.CameraFind.as_view(), name="camera_find"),

]
