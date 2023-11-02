from django.urls import path
from . import views


# This file is responsable for the urls provided


urlpatterns = [
    path('core/', views.core, name='core'),

    path('get_device_list_pop/', views.get_device_list_pop,
         name='get_device_list_pop'),

    path('get_service_list/', views.get_service_list,
         name='get_service_list'),

    path('get_device_list_paths/', views.get_device_list_paths,
         name='get_device_list_paths')

]
