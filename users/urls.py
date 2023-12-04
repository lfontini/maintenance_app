from django.urls import path
from . import views


# This file is responsable for the urls provided


urlpatterns = [
    path('login/', views.login, name='login'),


]
