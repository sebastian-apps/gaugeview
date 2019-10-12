from django.urls import path
from django.conf.urls import url, include
from . import views

app_name = 'core'

urlpatterns = [

    path('', views.gaugeview, name='gaugeview'),
    path('read_gauge/', views.read_gauge, name='read_gauge'),
    path('gauge_export/', views.gauge_export, name='gauge_export'),
]
