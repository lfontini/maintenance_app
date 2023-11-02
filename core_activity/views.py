from django.shortcuts import render, HttpResponse

# Create your views here.
from django.http import JsonResponse
from .forms import CoreForm
# Adicione isso para tratar mensagens de sucesso ou erro
from django.contrib import messages
from .retrive_services import List_services, list_all_devices_pop
from .quickbase_requests import get_paths_from_quickbase, get_serves_from_paths
import re
from .create_core_quickbase import Create_core_qb_main


def index(request):
    return HttpResponse("welcome!")


def core(request):
    form = CoreForm()
    if request.method == 'POST':
        form = CoreForm(data=request.POST)
        if form.is_valid():
            core_id = Create_core_qb_main(request.POST)
            print(request.POST)
            form.save()
            # Send success message to front end
            messages.success(
                request, f'Data was saceived successfully, Core number in Quickbase is {core_id}')

        else:
            # Mensagem de erro
            messages.error(
                request, 'Valid form, Please check it and try again or contact support None core was created')

    context = {'form': form}

    return render(request, 'index.html', context)


def get_service_list(request):
    DEVICE_NAME_STANDARD = r'^[A-Z0-9]{4}-[A-Z]{2}\d{1}$'

    DIA_STANDARD = r'[a-zA-Z0-9].{3,4}DIA[0-9]{1,2}'
    PATH_STANDARD = r'[a-zA-Z0-9]{4}(?:-[a-zA-Z0-9]{4})+'

    if request.method == 'POST':
        data = request.POST.get('data')
        devices = re.findall(DEVICE_NAME_STANDARD, data)
        internet_ids = re.findall(DIA_STANDARD, data)
        path = re.findall(PATH_STANDARD, data)
        print('devices:', devices)
        print('dias_encontrados:', internet_ids)
        print('data:', data)
        print('path:', path)
        if devices:
            services = List_services([devices[0]])
            data = {'services': services}
            print(data)
            return JsonResponse(data=data, safe=False)
        elif path:
            services = get_serves_from_paths(path[0])
            service_str = ' '.join(services['services'])
            data = {'services': service_str}
            print(data)
            return JsonResponse(data=data, safe=False)


def get_device_list_pop(request):
    '''
        This function is used to get the list of services from the gogs based a device as input 
        and return it as a json object.

    '''
    if request.method == 'POST':
        data = request.POST.get('data')
        if 'DIA' in data:
            services = list_all_devices_pop(data.split(".")[0])
        else:
            services = list_all_devices_pop(data)
        data = {'services': services}
        print(data)
    return JsonResponse(data)


def get_device_list_paths(request):
    network_list = request.POST.get('data')
    print(network_list)
    paths = get_paths_from_quickbase(network_list)
    data = {'services': paths}
    return JsonResponse(data=data, safe=False)
