from django.urls import path
from . import views
from django.views.generic import RedirectView
import os
from dotenv import load_dotenv

# This file is responsable for the urls provided


urlpatterns = [
    path('core/', views.core, name='core'),

    path('get_device_list_pop/', views.get_device_list_pop,
         name='get_device_list_pop'),

    path('get_service_list/', views.get_service_list,
         name='get_service_list'),

    path('get_device_list_paths/', views.get_device_list_paths,
         name='get_device_list_paths'),


    path('validation_core/', views.validation_core,
         name='validation_core'),

    path('test_services/', views.test_services,
         name='test_services'),

    path('troubleshooting_results/', views.troubleshooting_results,
         name='troubleshooting_results'),

    path('troubleshooting_services/', views.troubleshooting_services,
         name='troubleshooting_services'),

    path('perform_troubleshooting_services/', views.perform_troubleshooting_services,
         name='perform_troubleshooting_services'),

    path('compare_tests/', views.compare_tests,
         name='compare_tests'),


    path('close_tickets/', views.close_tickets,
         name='close_tickets'),

    path('close_tickets_zendesk/', views.close_tickets_zendesk,
         name='close_tickets_zendesk'),

    path('cancel_tickets_view/', views.cancel_tickets_view,
         name='cancel_tickets_view'),

    path('cancel_tickets_zendesk/', views.cancel_tickets_zendesk,
         name='cancel_tickets'),
 

    path('create_core/', views.create_core,
         name='create_core'),

    path('create_tickets/', views.create_tickets,
         name='create_tickets'),

    path('insert_services/', views.InsertServices,
         name='insert_services'),

     path('send_email/', views.SendEmail,
         name='send_email'),

   

     path('create_event_calendar/', views.CreateEventCalendar,
         name='create_event_calendar'),

     path('create_zabbix_maintenance/', views.CreateZabbixMaintenance,
         name='create_zabbix_maintenance'),
     
     path('documentation/', RedirectView.as_view(url=os.environ['DOCS_URL']), name='documentation'),


]
