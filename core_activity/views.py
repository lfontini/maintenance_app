from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import CoreForm
from django.contrib import messages
from .retrive_services import List_services, list_all_devices_pop
from .quickbase_requests import get_paths_from_quickbase, get_serves_from_paths
import re
from .create_core_quickbase import Create_core_qb_main
from .models import Core, Troubleshooting_registration
from .troubleshooting_services import get_services_affecteds
import datetime
from datetime import datetime
from .close_tickets_zendesk import close_ticket
from .test_cpe import Service_Validation
import logging


def troubleshooting_results(request):

    tests = Troubleshooting_registration.objects.values(
        'core_quickbase_id').distinct()

    context = {'tests': tests}

    return render(request, 'troubleshooting_results.html', context)


def compare_tests(request):
    core_id = request.POST.get('id')
    if core_id:
        tests = Troubleshooting_registration.objects.filter(
            core_quickbase_id=core_id).distinct()
        data = {'tests': list(tests.values(
            'date', 'circuito', 'resultadoping', 'interfacestatus'))}
        return JsonResponse(data=data, safe=False)

    data = {'tests': []}
    return JsonResponse(data=data, safe=False)


def validation_core(request):

    core = Core.objects.filter(status='Not Started')
    context = {'core': core}

    return render(request, 'core_validation.html', context)


def close_tickets(request):
    ''' 
        This function is only used for render template html 

    '''
    core = Core.objects.filter(status='Not Started')
    context = {'core': core}
    return render(request, 'close_tickets.html', context)


def core(request):
    form = CoreForm()

    if request.method == 'POST':
        form = CoreForm(data=request.POST)
        if form.is_valid():
            core_result = Create_core_qb_main(request.POST)
            logging.info('core_result: %s', core_result)

            if core_result:
                core_id = core_result.get('core_id')
                tickets = core_result.get('tickets')
                errors = core_result.get('errors')

                if core_id:
                    formulario = form.save(commit=False)
                    formulario.core_quickbase_id = core_id
                    formulario.tickets_zendesk_generated = tickets
                    formulario.save()

                    # Send success message to front end
                    messages.success(
                        request, f'Data was received successfully. Core number in Quickbase is {core_id}')

                    if errors:
                        messages.error(request=request, message=errors)

                    return redirect('validation_core')

                else:
                    messages.error(
                        request=request, message='Core was not created. Please check the provided data.')

            else:
                messages.error(
                    request=request, message='Core creation failed. Please try again or contact support.')

        else:
            # Form is invalid
            error_details = ', '.join(
                [f'{field}: {error}' for field, error in form.errors.items()])
            messages.error(
                request, f'Invalid form. Please check the following fields: {error_details}. None core was created')

    context = {'form': form}
    return render(request, 'create_core.html', context)


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
            return JsonResponse(data=data, safe=False)
        elif path:
            services = get_serves_from_paths(path[0])
            service_str = ' '.join(services['services'])
            data = {'services': service_str}
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
    return JsonResponse(data)


def get_device_list_paths(request):
    network_list = request.POST.get('data')
    print(network_list)
    paths = get_paths_from_quickbase(network_list)
    data = {'services': paths}
    return JsonResponse(data=data, safe=False)


def troubleshooting_services(request):
    return render(request=request, template_name='troubleshooting_open.html')


def test_services(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        print('ID recebido do frontend:', data_id)

        try:
            # Obtenha os serviços afetados usando a função importada
            results = get_services_affecteds(data_id)
            for result in results:
                print(type(result), 'result')
                if result != None:
                    for key, value in result.items():
                        print('circuito', key, value)
                        registros = Troubleshooting_registration(
                            core_quickbase_id=data_id,
                            circuito=result['circuito'],
                            resultadoping=result['resultadoping'],
                            status=result['status'],
                            interfacestatus=result['interfacestatus'],
                            statusquickbase=result['statusquickbase'],
                        )
                        registros.save()

            data = {'services': results}

            # Envie a resposta JSON
            return JsonResponse(data, safe=False)

        except Core.DoesNotExist:
            # Lide com o caso em que o Core com o ID fornecido não existe
            return JsonResponse({'error': 'Core não encontrado para o ID fornecido'}, status=404)

    # Se a requisição não for POST, retorne um JsonResponse indicando o método não permitido
    return JsonResponse({'error': 'Método não permitido'}, status=405)


def close_tickets_zendesk(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        query = Core.objects.filter(id=id)

        # Check if the query returned any results
        if query.exists():
            # Retrieve the first instance from the query
            core_instance = query.first()

            # Process the tickets
            tickets = core_instance.tickets_zendesk_generated.strip().split(',')

            result = close_ticket(tickets)

            if result is not None:
                # Update the status of the retrieved instance
                core_instance.status = "completed"

                # Save the changes to the database
                core_instance.save()

                return JsonResponse({'success': 'Ticket(s) {} zendesk for core {} were closed'.format(result, id)})

        return JsonResponse({'error': 'Core with ID {} not found'.format(id)}, status=404)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


def perform_troubleshooting_services(request):
    id = request.POST.get('circuitos')
    result = Service_Validation(id)
    print(result)
    return JsonResponse({'results': result})
