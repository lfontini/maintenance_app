from django.http import StreamingHttpResponse

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
        result = Create_core_qb_main(request.POST)

        def stream_response():
            yield """
            <html>
            <head>
                <meta charset='utf-8'>
            </head>
            <body style='background: linear-gradient(#000000, #192655); margin: 0; padding: 0; display: flex; align-items: center; justify-content: center; height: 100vh;'>
                <div style='background-color: rgb(255 255 255 / 36%); '>
                    <h1 style='text-align: center; color: rgb(255 255 255 / 36%) ;'>Core Processing Results</h1>
                    <ul style='list-style-type: none; padding: 0;'>

            """
            error_format = ";[]'',"
            for chunk in result:
                if 'Errors' in chunk:
                    data = chunk.split(",")
                    for item in data:
                        yield f"<li style='color: black; min-width: 1000px;max-width: 1000px; padding: 5px; background-color: rgb(255 255 255 / 36%);font-family: sans-serif; '>{item}<span style='margin-left: 20px;'>❌</span></li>\n"
                else:
                    yield f"                        <li style='color: black; min-width: 1000px;max-width: 1000px; padding: 5px;  background-color: rgb(255 255 255 / 36%);font-family: sans-serif; '>{chunk}<span style='margin-left: 20px;'>&#10003</span></li>\n"

            yield """
                    </ul>
                                <button onclick='goBack()' style='margin-top: 20px; background-color: #39A7FF; color: black; padding: 10px; border: none; cursor: pointer;'>Go Back</button>
                            </div>

                            <script>
                                function goBack() {
                                    window.location.href = "/core";
                                }
                            </script>
                        </body>
                        </html>
                """

        response = StreamingHttpResponse(
            streaming_content=stream_response(), content_type="text/html")
        response["Cache-Control"] = "no-cache"

        return response

    context = {'form': form}

    return render(request, 'create_core.html', context)


def get_service_list(request):

    DEVICE_NAME_STANDARD = r'^[A-Z0-9]{3,}-[A-Z]+[0-9]{0,}$'

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
                if result != None:
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
            print('ticketssssssssssssssssssssssss', tickets)
            result = cancel_tickets(tickets)

            if result is not None:
                # Update the status of the retrieved instance
                core_instance.status = "completed"

                # Save the changes to the database
                core_instance.save()

                return JsonResponse({'success': 'Ticket(s) {} zendesk for core {} were closed'.format(result, id)})

        return JsonResponse({'error': 'Core with ID {} not found'.format(id)}, status=404)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


def comparar_strings(string_anterior, string_posterior):

    pattern = re.compile(r'Upload: (\d+), Download: (\d+)')

    # Encontrar correspondências nas strings
    match_anterior = pattern.search(string_anterior)
    match_posterior = pattern.search(string_posterior)

    # Verificar se houve correspondências e extrair os números
    if match_anterior and match_posterior:
        upload_anterior = int(match_anterior.group(1))
        download_anterior = int(match_anterior.group(2))

        upload_posterior = int(match_posterior.group(1))
        download_posterior = int(match_posterior.group(2))

        # Verificar se os valores estão próximos
        if upload_anterior and upload_posterior and download_anterior and download_posterior != 0:
            return True
        else:
            return False
    elif 'None data retrived' in string_anterior and string_posterior:
        print("None data retrived")
        return None
    else:
        print("nao foi possivel avaliar as strings")
        return False


def verificar_circuitos(circuitos_ok, circuitos_nok, circuitos_inconclusive):
    percentual_ok = (len(circuitos_ok) /
                     (len(circuitos_ok) + len(circuitos_nok) + len(circuitos_inconclusive))) * 100

    percentual_nok = (len(circuitos_nok) /
                      (len(circuitos_ok) + len(circuitos_nok) + len(circuitos_inconclusive))) * 100

    percentual_inc = (len(circuitos_inconclusive) /
                      (len(circuitos_ok) + len(circuitos_nok) + len(circuitos_inconclusive))) * 100
    print("Circuitos OK:", len(circuitos_ok))
    print("Circuitos NOK:", len(circuitos_nok))
    print("Circuitos inconclusivo:", len(circuitos_inconclusive))

    print('Percentual de circuitos OK: {:.2f}%'.format(percentual_ok))
    print('Percentual de circuitos NOK: {:.2f}%'.format(percentual_nok))
    print('Percentual de circuitos INC : {:.2f}%'.format(percentual_inc))
    if percentual_ok >= 50:
        print("Mais de 50% dos circuitos estão OK. Tudo OK!")
        response = "Tudo OK!"
    else:
        response = "Percentual abaixo de 50%."

    return 'Percentual de circuitos OK: {:.2f}%'.format(percentual_ok)


def valid_services(request):
    # Supondo que Core seja um modelo Django
    core = Core.objects.filter(id="44")

    # Convert start and end date strings to datetime objects
    start_date_activity_core = datetime.strptime(
        core[0].start_date.strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M"
    )
    end_date_activity_core = datetime.strptime(
        core[0].end_date.strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M"
    )

    tests = Troubleshooting_registration.objects.filter(
        core_quickbase_id="44").order_by('-circuito')

    atividade_anterior_list = []
    atividade_posterior_list = []

    for test in tests:
        # Convert test.date to datetime object if needed
        test_date = datetime.strptime(
            test.date.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"
        )

        if test_date < start_date_activity_core:
            atividade_anterior_list.append(test)
            print("Test realizado antes da atividade")
        elif test_date > end_date_activity_core:
            atividade_posterior_list.append(test)
            print("Test realizado depois da atividade")

    circuitos_ok = set()
    circuitos_nok = set()
    circuitos_inconclusive = set()

    print(len(atividade_anterior_list), len(atividade_posterior_list))
    for atividade_posterior in atividade_posterior_list:
        for atividade_anterior in atividade_anterior_list:
            print(atividade_posterior.circuito, atividade_anterior.circuito)
            if atividade_posterior.circuito == atividade_anterior.circuito:
                # Supondo que comparar_strings seja uma função adequada
                print("Interface status inicial:", atividade_anterior.interfacestatus,
                      "Interface status Final:", atividade_posterior.interfacestatus)

                result_comparation = comparar_strings(
                    atividade_anterior.interfacestatus, atividade_posterior.interfacestatus)
                if result_comparation is True:
                    circuitos_ok.add(atividade_anterior.circuito)
                elif result_comparation is False:
                    circuitos_nok.add(atividade_anterior.circuito)
                else:
                    circuitos_inconclusive.add(atividade_anterior.circuito)
            else:
                print("As strings são diferentes.")
        else:
            print("circuitos diferentes")
    verificar_circuitos(circuitos_ok, circuitos_nok, circuitos_inconclusive)

    return None
