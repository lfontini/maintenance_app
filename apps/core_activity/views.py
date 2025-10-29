from .zabbix_maintenance_create import create_zabbix_maintenance
from .google_calendar_create_events import CreateCalendarEvent
import time
from .Send_emails import EmailNotification
import json
from django.shortcuts import render
from django.http import JsonResponse
from .forms import CoreForm
from .retrive_services import List_services, list_all_devices_pop
from .quickbase_requests import get_paths_from_quickbase, get_serves_from_paths
import re
from .create_core_quickbase import Create_core_qb_main
from .models import Core, Troubleshooting_registration
from .troubleshooting_services import get_services_affecteds
import datetime
from datetime import datetime
from .close_tickets_zendesk import close_ticket
from .cancel_tickets_zendesk import cancel_tickets
from .test_cpe import Service_Validation
from .zabbix_maintenance_delete import delete_maintenance_zabbix
from .insert_services_core import insert_services_into_existent_core
from .generate_tickets_zendesk import generate_tickets_zendesk


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
    View to render a template displaying all 'Not Started' core tickets.

    This function queries the Core model to retrieve all tickets with a status of 'Not Started'.
    Then, it renders a template named 'close_tickets.html', passing the retrieved tickets as context.

    Args:
        request: HTTP request object.

    Returns:
        HTTP response with the rendered template.
    '''
    # Filter all cores with status not Started
    core = Core.objects.filter(status='Not Started')
    # get all data and send to template html
    context = {'core': core}
    return render(request, 'close_tickets.html', context)


def core(request):
    ''' 
    View to render a template displaying a form for creating a Core object.

    This function initializes a new instance of CoreForm, which is used to render
    a form in the template 'create_core.html'.

    Args:
        request: HTTP request object.

    Returns:
        HTTP response with the rendered template containing the form.
    '''
    form = CoreForm()

    context = {'form': form}

    return render(request, 'create_core.html', context)


def get_service_list(request):
    ''' 
        this function receive the element network link or router or DIA or POP and 
        get the services from quickbase in case network link or gogs in case router or pop 

        return path if network were choosen 
        return router if DIA or POP were choosen 

    '''
    DEVICE_NAME_STANDARD = r'[a-zA-Z0-9]{4}-[ARASWLSRLERCR]{2,3}[0-9]'

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
            print(len(results))
            for result in results:
                print(type(result), 'result')
                print(result, 'result')
                if result != None:
                    core_quickbase_id = data_id,
                    circuito = result.get('circuito'),
                    resultadoping = result.get('resultadoping'),
                    status = result.get('status'),
                    interfacestatus = result.get('interfacestatus'),
                    statusquickbase = result.get('statusquickbase'),
                    if core_quickbase_id and circuito and resultadoping and status and interfacestatus and statusquickbase:
                        registros = Troubleshooting_registration(
                            core_quickbase_id=data_id,
                            circuito=result.get('circuito'),
                            resultadoping=result.get('resultadoping'),
                            status=result.get('status'),
                            interfacestatus=result.get('interfacestatus'),
                            statusquickbase=result.get('statusquickbase'),
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
            zabbix_maintenance_id = core_instance.zabbix_maintenance_id

            result = close_ticket(tickets)
            # check if contains zabbix mantenanceid registered into zabbix
            if zabbix_maintenance_id.isdigit():
                zabbix_result = delete_maintenance_zabbix(
                    zabbix_maintenance_id)
                print(zabbix_result)
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


def cancel_tickets_view(request):
    core = Core.objects.filter(status='Not Started')
    context = {'core': core}
    return render(request, 'cancel_tickets.html', context)


def cancel_tickets_zendesk(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        query = Core.objects.filter(id=id)

        # Check if the query returned any results
        if query.exists():
            # Retrieve the first instance from the query
            core_instance = query.first()
            # Process the tickets
            tickets = core_instance.tickets_zendesk_generated.strip().split(',')
            result = cancel_tickets(tickets)

            if result is not None:
                # Update the status of the retrieved instance
                core_instance.status = "completed"

                # Save the changes to the database
                core_instance.save()

                return JsonResponse({'success': 'Ticket(s) {} zendesk for core {} were closed'.format(result, id)})

        return JsonResponse({'error': 'Core with ID {} not found'.format(id)}, status=404)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


def create_core(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        error = None
        result = Create_core_qb_main(data)
        if 'core_id' and 'id' in result:
            core_id = result.get('core_id')
            id = result.get('id')
            response_data = {
                'core_id': core_id,
                'id': id,
                'error': error}
            print(response_data)
            return JsonResponse(response_data)
        else:
            response_data = {
                'result': result}
            return JsonResponse(response_data, status=400)

    return JsonResponse({'error': 'Método não permitido'}, status=405)


def create_tickets(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        ticket = generate_tickets_zendesk(data)
        customer_prefix = data.get('prefix')

        response_data = {
            'result': f'Successfully generated  {ticket} customer {customer_prefix}',
            'ticket_id': ticket}
        return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid post '}, status=405)


def InsertServices(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        services = data.get('services')
        core_id = data.get('core_id')
        services = insert_services_into_existent_core(
            core_id=core_id, service_data=services)
        core_id = core_id
        response_data = {
            'result': f'Insered services into core {core_id} successfully'}
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Invalid post '}, status=400)


def SendEmail(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        core_id = data.get('core_id')
        tickets = data.get('tickets')
        start_date = data.get('start_date')

        email = EmailNotification()
        email.send_notification(core_id=core_id,
                                tickets=tickets,
                                date=start_date)

        response_data = {
            'result': f'Genetated Email successfully for core {core_id}'}
        return JsonResponse(response_data)

    else:
        return JsonResponse({'error': 'Invalid post '}, status=400)


def CreateEventCalendar(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        affected_services = data.get('affected_services')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        print(data)
        kwargs = {
            'get_services_affecteds': affected_services,
            'start_date': start_date,
            'end_date': end_date,
        }

        response = CreateCalendarEvent(**kwargs)
        print(response)
        response_data = {
            'result': f'Generated Calendar event successfullly '}
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Invalid post '}, status=400)


def CreateZabbixMaintenance(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        core_id = data.get('core_id')
        start_maintenance = data.get('start_date')
        end_maintenance = data.get('end_date')
        services = data.get('services')
        id = data.get('id')

        zabbix_maintenance_id = create_zabbix_maintenance(id=id,
                                                          services=services,
                                                          start_maintenance=start_maintenance,
                                                          end_maintenance=end_maintenance,
                                                          core_id=core_id)

        response_data = {
            'result': f'Generated Zabbix Maintenance {zabbix_maintenance_id} '}
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Invalid post '}, status=400)
