from celery import shared_task
from datetime import datetime
from time import sleep
from .models import Core, Troubleshooting_registration
from .troubleshooting_services import get_services_affecteds
import re
from .close_tickets_zendesk import close_ticket
from .zabbix_maintenance_delete import delete_maintenance_zabbix
# help to setup celery https://www.youtube.com/watch?v=EfWa6KH8nVI


def verificar_circuitos(services_ok, services_nok, services_inconclusive):
    percentual_ok = 0
    percentual_nok = 0
    percentual_inc = 0
    if len(services_ok) != 0:
        percentual_ok = (len(services_ok) /
                         (len(services_ok) + len(services_nok) + len(services_inconclusive))) * 100
    if len(services_nok) != 0:
        percentual_nok = (len(services_nok) /
                          (len(services_ok) + len(services_nok) + len(services_inconclusive))) * 100
    if len(services_inconclusive) != 0:
        percentual_inc = (len(services_inconclusive) /
                          (len(services_ok) + len(services_nok) + len(services_inconclusive))) * 100

    if len(services_ok):
        print("services OK:", len(services_ok), services_ok)
    if len(services_nok):
        print("services NOK:", len(services_nok), services_nok)
    if len(
            services_inconclusive):
        print("services inconclusivo:", len(
            services_inconclusive), services_inconclusive)

    print('Percentual de services OK: {:.2f}%'.format(percentual_ok))
    print('Percentual de services NOK: {:.2f}%'.format(percentual_nok))
    print('Percentual de services INC : {:.2f}%'.format(percentual_inc))
    if percentual_ok >= 50:
        print("More then 50% of services are OK")
        return True, 'Percentual of services OK: {:.2f}%'.format(percentual_ok)
    else:
        return False, 'Percentual of services OK: {:.2f}%'.format(percentual_ok)


def compare_service_tests(anterior_test_service, posterior_test_service):

    pattern = re.compile(r'Upload: (\d+), Download: (\d+)')

    # Encontrar correspondências nas strings
    match_anterior = pattern.search(anterior_test_service)
    match_posterior = pattern.search(posterior_test_service)

    # Verificar se houve correspondências e extrair os números
    if match_anterior and match_posterior:
        upload_anterior = int(match_anterior.group(1))
        download_anterior = int(match_anterior.group(2))

        upload_posterior = int(match_posterior.group(1))
        download_posterior = int(match_posterior.group(2))

        # check if all vars have traffic numbers
        if upload_anterior and upload_posterior and download_anterior and download_posterior != 0:
            return True
        else:
            return False
    elif 'None data retrived' in anterior_test_service and posterior_test_service:
        print("None data retrived")
        return None
    else:
        print("impossible to check services")
        return False


@shared_task
def test_services(core_id):

    results = get_services_affecteds(core_id)

    for result in results:
        print(type(result), 'result')
        if result != None:
            print(result['statusquickbase'][0])
            registros = Troubleshooting_registration(
                core_quickbase_id=core_id,
                circuito=result['circuito'],
                resultadoping=result['resultadoping'],
                status=result['status'],
                interfacestatus=result['interfacestatus'],
                statusquickbase=result['statusquickbase'][0],
            )
            registros.save()
    return results


@shared_task
def valid_services(id):
    ''' 

    This function is trigged by celery and it will perform a final test comparing 
    tests executed before activity and after activity and give some analisys 
    ex 
    services ok = list           -----> services who have traffic before and after act
    service nok = list            -----> services who do not have traffic before and after act
    services_inconclusive = list  -----> services who it was impossible to access or test properly

    '''
    core = Core.objects.filter(id=id)[0]
    tickets = core.tickets_zendesk_generated.strip().split(',')
    zabbix_maintenance_id = core.zabbix_maintenance_id

    # Convert start and end date strings to datetime objects
    start_date_activity_core = datetime.strptime(
        core.start_date.strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M"
    )
    end_date_activity_core = datetime.strptime(
        core.end_date.strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M"
    )

    tests = Troubleshooting_registration.objects.filter(
        core_quickbase_id=id).order_by('-circuito')

    previous_activity_list = []
    after_acitivity_list = []

    for test in tests:
        # Convert test.date to datetime object if needed
        test_date = datetime.strptime(
            test.date.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"
        )

        # separe into two lists test perfomred before and after activity
        if test_date < start_date_activity_core:
            previous_activity_list.append(test)
        elif test_date > end_date_activity_core:
            after_acitivity_list.append(test)

    services_ok = set()
    services_nok = set()
    services_inconclusive = set()

    print('after_acitivity_list', len(after_acitivity_list))
    print('previous_activity_list', len(previous_activity_list))

    for after_acitivity in after_acitivity_list:
        for previous_activity in previous_activity_list:
            print(previous_activity)
            if after_acitivity.circuito == previous_activity.circuito:
                # compare if services are the same
                result_comparation = compare_service_tests(
                    previous_activity.interfacestatus, after_acitivity.interfacestatus)
                if result_comparation is True:
                    services_ok.add(previous_activity.circuito)
                elif result_comparation is False:
                    services_nok.add(previous_activity.circuito)
                else:
                    services_inconclusive.add(previous_activity.circuito)
            else:
                print("services are different")

    final_result = verificar_circuitos(
        services_ok, services_nok, services_inconclusive)
    if final_result[0] == True:
        # only change the maintenance status if tests performed well
        core.status = "completed"
        core.save()
        if tickets:
            result = close_ticket(tickets)
            print(result)
        if zabbix_maintenance_id.isdigit():
            zabbix_result = delete_maintenance_zabbix(
                zabbix_maintenance_id)
            print(zabbix_result)
        return final_result
    else:
        return f"Error to close the maintenance {final_result}"
