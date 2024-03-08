from celery import shared_task
from datetime import datetime
from time import sleep
from .models import Core, Troubleshooting_registration
from .troubleshooting_services import get_services_affecteds
import re
from .close_tickets_zendesk import close_ticket
from .zabbix_maintenance_delete import delete_maintenance_zabbix
# help to setup celery https://www.youtube.com/watch?v=EfWa6KH8nVI


def check_services(services_ok, services_nok):
    """
    Checks the status of services and calculates percentages.

    Args:
    services_ok (list): List of services marked as OK.
    services_nok (list): List of services marked as NOK.

    Returns:
    tuple: A tuple containing a boolean indicating whether more than 50% of services are OK,
           and a message with the percentage of services marked as OK.
    """
    total_services = len(services_ok) + len(services_nok)
    try:
        percentual_ok = 0
        percentual_nok = 0

        # Calculate percentages only if lists are not empty to avoid division by zero
        if len(services_ok) != 0:
            percentual_ok = (len(services_ok) / total_services) * 100
        if len(services_nok) != 0:
            percentual_nok = (len(services_nok) / total_services) * 100

        # Print information about the services
        if services_ok:
            print("Services OK:", len(services_ok), services_ok)
        if services_nok:
            print("Services NOK:", len(services_nok), services_nok)

        # Print percentages
        print('Percentage of services OK: {:.2f}%'.format(percentual_ok))
        print('Percentage of services NOK: {:.2f}%'.format(percentual_nok))

        # Check if more than 50% of services are OK
        if percentual_ok >= 30:
            print("More than 30% of services are OK")
            return True, 'Percentage of services OK: {:.2f}%'.format(percentual_ok)
        else:
            print("Less than 50% of services are OK")
            return False, 'Percentage of services OK: {:.2f}%'.format(percentual_ok)

    except ZeroDivisionError:
        print("Error: Division by zero.")
        return False, "Error: Division by zero."
    except Exception as e:
        print("An error occurred:", e)
        return False, "An error occurred."


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
                else:
                    services_nok.add(previous_activity.circuito)
            else:
                print("services are different")

    final_result = check_services(
        services_ok, services_nok, )
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
