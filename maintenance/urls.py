from django.urls import path
from . import views

urlpatterns = [

    path('', views.index, name='index'),

    path('maintenance/', views.maintenance, name='maintenance'),
    # Outras URLs do aplicativo podem ser definidas aqui
]
