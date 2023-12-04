from django.shortcuts import render, redirect
from django.contrib.auth.models import User

# Create your views here.


def login(request):
    usuarios = User.objects.all()
    for user in usuarios:
        print(user)
    return render(request, 'login.html')
