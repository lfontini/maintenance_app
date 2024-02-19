import requests
from datetime import datetime
import os
from dotenv import load_dotenv
from .quickbase_requests import Get_service_info
import re
import concurrent.futures
from .generate_tickets_zendesk import generate_tickets_zendesk
from .Send_emails import EmailNotification
from .google_calendar_create_events import EventCreator
from .quickbase_requests import fetch_activity_data, get_customers_contact, get_services_from_nni
from .zabbix_maintenance_create import create_zabbix_maintenance
from multiprocessing.pool import ThreadPool
from .forms import CoreForm


# load enviroments variables
load_dotenv()
HOSTNAME_QB = os.environ.get("HOSTNAME_QB")
TOKEN_QB = os.environ.get("TOKEN_QB")


def Make_quickbase_request(data):
    print(data)
    headers = {
        'QB-Realm-Hostname': HOSTNAME_QB,
        'User-Agent': '{User-Agent}',
        'Authorization': TOKEN_QB
    }
    print(headers)
    body = {"to": "bk32qj72c", "data": [data], "fieldsToReturn": [3]}
    r = requests.post(
        'https://api.quickbase.com/v1/records',
        headers=headers,
        json=body
    )
    print(r.json())
    if r.status_code == 200:
        response = r.json()
        if 'data' in response:
            if response['data']:
                for field in response['data']:
                    id = field['3']['value']
                    return id

    return None


def identify_services(raw_data):
    service_info = {}
    services = set(re.findall(
        r'[a-zA-Z0-9]{3}\.[0-9]{3,5}\.[a-zA-Z][0-9]{3}', raw_data))
    print(len(services))
    nnis = set(re.findall(
        r'[a-zA-Z0-9]{3}\.[0-9]{3,5}\.[N][0-9]{3}', raw_data))

    if nnis:
        for nni in nnis:
            print('incluso nni', nni)
            list_services_nni = get_services_from_nni(nni)
            if list_services_nni:
                services.update(list_services_nni)
            else:
                print(f"Not service attached in {nni}")
    if services:
        prefixes_and_contacts = {}

        def process_prefix(prefix):
            prefixes_and_contacts[prefix] = get_customers_contact(prefix)

        prefixes = []
        for service in services:
            print("checando ... ", service)
            prefixe = service.split(".")[0]
            if prefixe not in prefixes:
                prefixes.append(prefixe)
        # Use concurrent.futures para processar os prefixos em paralelo
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(process_prefix, prefixes)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit tasks for each service to the executor
            future_to_service = {executor.submit(
                Get_service_info, service): service for service in services}
            # Wait for the tasks to complete and collect the results
            for future in concurrent.futures.as_completed(future_to_service):
                service = future_to_service[future]
                print("completou a task ")
                try:
                    service_info[service] = future.result()
                except Exception as e:
                    print(f"Error fetching info for {service}: {e}")

        return service_info, prefixes_and_contacts
    else:
        return None, None


def insert_service(service, core_id, service_data):
    if service_data:
        id = service_data.get('id', None)
        status = service_data.get('status', None)

        if status == "Delivered":
            print(f"Inserting service {service} into core {core_id}")
            headers = {
                'QB-Realm-Hostname': HOSTNAME_QB,
                'User-Agent': '{User-Agent}',
                'Authorization': TOKEN_QB
            }

            body = {
                "to": "bmniuvke2",
                "data": [{"8": {"value": id}, "10": {"value": core_id}}],
                "fieldsToReturn": [10, 9]
            }

            response = requests.post(
                'https://api.quickbase.com/v1/records', headers=headers, json=body)

            if response.status_code == 200:
                return f'service {service} inserted into core {core_id}'
        else:
            print(f"Service {service} is not delivered. STATUS: {status}")
        return None


def Insert_services_into_existent_core(core_id, services):
    yield f"inserindo servicos"
    num_threads = 4

    def insert_service_wrapper(service):
        return insert_service(service, core_id, services[service])

    # Use ThreadPool para executar a função insert_service em threads concorrentes
    with ThreadPool(num_threads) as pool:
        results = pool.map(insert_service_wrapper, services)

    return results


def Ajust_Core_date(date):
    ''' 

        This function receive a date and return a new date 

    '''
    currunt_date = datetime.strptime(date, "%Y-%m-%dT%H:%M")
    new_date_formatted = currunt_date.strftime("%Y-%m-%dT%H:%M:%S")

    return new_date_formatted


def CreateCalendarEvent(**kwargs):
    get_services_affecteds = kwargs.get('get_services_affecteds')
    start_date = kwargs.get('start_date')
    end_date = kwargs.get('end_date')
    element = kwargs.get('element')

    description_calendar = f''' 
    A core activity will be performed and will affect services below \n
    {get_services_affecteds}

    '''
    formated_start_data = Ajust_Core_date(
        start_date)

    formated_end_data = Ajust_Core_date(
        end_date)

    event_creator = EventCreator(calendar_title=f'Planned Work Maintenance {element[0][0]}',
                                 start_time=formated_start_data,
                                 end_time=formated_end_data,
                                 description=description_calendar)
    event_creator.create_event()
    return event_creator


def Calc_duration_time_core(start_date, end_date):
    ''' 
    This function takes two dates and returns the duration between them in milliseconds.
    '''
    start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M")
    end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M")
    duration = end_date - start_date
    duration_seconds = duration.total_seconds()

    # Convert the duration to milliseconds
    duration_milliseconds = int(duration_seconds * 1000)

    return duration_milliseconds


def Create_core_qb_main(data):
    form = CoreForm(data=data)
    if form.is_valid():
        validacao = form.is_valid()
        print('Validated form successfully', )
        yield 'Validated form successfully'

        activity_type = data.get('activity_type')
        activity_related_to = data.get('activity_related_to')
        common_fields = {
            'ign_engineer': data.get('ign_engineer'),
            'internet_id': data.get('internet_id'),
            'status': data.get('status'),
            'start_date': data.get('start_date'),
            'end_date': data.get('end_date'),
            'duration': data.get('duration'),
            'downtime': data.get('downtime'),
            'Description': data.get('Description'),
            'Description_to_customers': data.get('Description_to_customers'),
            'affected_services': data.get('affected_services'),
            'location': data.get('location'),
        }

        new_date_formatted = Ajust_Core_date(common_fields['start_date'])
        duration_activity = Calc_duration_time_core(
            common_fields['start_date'], common_fields['end_date'])
        remote_hands_information = data.get('remote_hands_information')

        if activity_type == 'from_ign' or activity_type == 'from_vendor':
            if activity_related_to == 'internet_service':
                internet_id = data.get('internet_id')
                internet_name = fetch_activity_data(database="bjx5t3hbx", fields=[
                    6], where="{3.EX." + f"'{internet_id}'"+"}")
                print(internet_name)
                new_date_formatted = Ajust_Core_date(
                    common_fields['start_date'])
                duration_activity = Calc_duration_time_core(
                    common_fields['start_date'], common_fields['end_date'])
                ign_engineer = data.get('ign_engineer')
                print('data normal ', common_fields['start_date'])
                core_data = {
                    "6": {"value": new_date_formatted},
                    "8": {"value": common_fields['Description']},
                    "11": {"value": duration_activity},
                    "34": {"value": {"id": ign_engineer}},
                    "51": {"value": internet_id},
                    "43": {"value": "From IGN"},
                    "44": {"value": "Internet Service"},
                    "89": {"value": common_fields['status']},
                    "97": {"value": common_fields['location']},
                    "98": {"value": remote_hands_information}

                }
                print('core_data', core_data)
                # core_id = Make_quickbase_request(core_data)
                core_id = '1112'
                if core_id:
                    formulario = form.save(commit=False)
                    formulario.core_quickbase_id = core_id
                    formulario.save()
                    yield f'Generated core {core_id}'

                    identified_services, prefixes_and_contacts = identify_services(
                        common_fields['affected_services'])

                    yield f'Fetching data for identified services'
                    if identified_services:
                        services = Insert_services_into_existent_core(
                            core_id, identified_services)
                        yield f'Inserted services into Quickbase core'

                        if services is not None:
                            tickets, errors = generate_tickets_zendesk(identified_services,
                                                                       common_fields['start_date'], common_fields['end_date'],
                                                                       common_fields['downtime'],  common_fields['location'], description=common_fields['Description_to_customers'], prefixes_and_contacts=prefixes_and_contacts, core_id=core_id)
                            yield f'Generated tickets in Zendesk: {tickets}'
                            yield f'Errors to open tickets in Zendesk: {errors}'

                            if tickets:
                                formulario.tickets_zendesk_generated = tickets
                                formulario.save()
                                email = EmailNotification()
                                email.send_notification(
                                    core_id=core_id, tickets=tickets, date=common_fields['start_date'])

                                # prepar data for scheduling calendar
                                kwargs = {
                                    'get_services_affecteds': common_fields['affected_services'],
                                    'start_date': common_fields['start_date'],
                                    'end_date':  common_fields['end_date'],
                                    'element': [[internet_name[0][0]]]
                                }

                                # Chamar a função CreateCalendarEvent com os argumentos passados como kwargs
                                print("chamando khards", kwargs)
                                CreateCalendarEvent(**kwargs)

                                yield f'Created event in Google Calendar'

                                zabbix_maintenance_id = create_zabbix_maintenance(services=identified_services,
                                                                                  start_maintenance=common_fields[
                                                                                      'start_date'],
                                                                                  end_maintenance=common_fields['end_date'],
                                                                                  core_id=core_id)
                                formulario.zabbix_maintenance_id = zabbix_maintenance_id
                                formulario.save()
                                yield f'Created maintenance window in Zabbix for the services'
                    else:
                        yield 'No identified services to include'

                else:
                    yield 'Error to open core'
                    return None

        if activity_related_to == 'network_link':
            network_link = data.get('network_link')
            network_link_name = fetch_activity_data(database="bjvepudtt", fields=[
                7], where="{3.EX." + f"'{network_link}'"+"}")
            print(network_link_name)
            new_date_formatted = Ajust_Core_date(common_fields['start_date'])
            duration_activity = Calc_duration_time_core(
                common_fields['start_date'], common_fields['end_date'])
            ign_engineer = data.get('ign_engineer')

            core_data = {
                "6": {"value": new_date_formatted},
                "8": {"value": common_fields['Description']},
                "11": {"value": duration_activity},
                "34": {"value": {"id": ign_engineer}},
                "48": {"value": network_link},
                "43": {"value": "From IGN"},
                "44": {"value": "Network Link"},
                "89": {"value": common_fields['status']},
                "97": {"value": common_fields['location']},
                "98": {"value": remote_hands_information}
            }
            # core_id = Make_quickbase_request(core_data)
            core_id = '1958'
            if core_id:
                formulario = form.save(commit=False)
                formulario.core_quickbase_id = core_id
                formulario.save()
                yield f'Generated core {core_id}'

                identified_services, prefixes_and_contacts = identify_services(
                    common_fields['affected_services'])

                yield f'Fetching data for identified services'

                if identified_services:
                    services = Insert_services_into_existent_core(
                        core_id, identified_services)
                    yield f'Inserted services into Quickbase core'

                    if services is not None:
                        tickets, errors = generate_tickets_zendesk(identified_services,
                                                                   common_fields['start_date'], common_fields['end_date'],
                                                                   common_fields['downtime'],  common_fields['location'], description=common_fields['Description_to_customers'], prefixes_and_contacts=prefixes_and_contacts, core_id=core_id)
                        yield f'Generated tickets in Zendesk: {tickets}'
                        yield f'Errors to open tickets in Zendesk: {errors}'

                    if tickets:
                        formulario.tickets_zendesk_generated = tickets
                        formulario.save()
                        email = EmailNotification()
                        email.send_notification(
                            core_id=core_id, tickets=tickets, date=common_fields['start_date'])

                        kwargs = {
                            'get_services_affecteds': common_fields['affected_services'],
                            'start_date': common_fields['start_date'],
                            'end_date':  common_fields['end_date'],
                            'element': [[network_link_name[0][0]]]
                        }
                        CreateCalendarEvent(**kwargs)

                        yield f'Created event in Google Calendar'

                        zabbix_maintenance_id = None
                        zabbix_maintenance_id = create_zabbix_maintenance(services=identified_services,
                                                                          start_maintenance=common_fields[
                                                                              'start_date'],
                                                                          end_maintenance=common_fields['end_date'],
                                                                          core_id=core_id)
                        if zabbix_maintenance_id:
                            formulario.zabbix_maintenance_id = zabbix_maintenance_id
                            formulario.save()
                            yield f'Created maintenance window in Zabbix for the services'
                        else:
                            yield f'Erro to create maintenance window in Zabbix for the services'
                    else:
                        yield 'No identified services to include'
            else:
                yield 'Error to open core'
                return None

        if activity_related_to == 'pop':
            pop = data.get('pop')
            pop_name = fetch_activity_data(database="bjvepsjqq", fields=[
                8], where="{3.EX." + f"'{pop}'"+"}")
            print(pop_name)
            new_date_formatted = Ajust_Core_date(common_fields['start_date'])
            duration_activity = Calc_duration_time_core(
                common_fields['start_date'], common_fields['end_date'])
            ign_engineer = data.get('ign_engineer')

            core_data = {
                "6": {"value": new_date_formatted},
                "8": {"value": common_fields['Description']},
                "11": {"value": duration_activity},
                "34": {"value": {"id": ign_engineer}},
                "40": {"value": pop},
                "43": {"value": "From IGN"},
                "44": {"value": "POP"},
                "89": {"value": common_fields['status']},
                "97": {"value": common_fields['location']},
                "98": {"value": remote_hands_information}
            }
            # core_id = Make_quickbase_request(core_data)
            core_id = '1958'
            if core_id:
                formulario = form.save(commit=False)
                formulario.core_quickbase_id = core_id
                formulario.save()
                yield f'Generated core {core_id}'

                identified_services, prefixes_and_contacts = identify_services(
                    common_fields['affected_services'])

                yield f'Fetching data for identified services'

                if identified_services:
                    services = Insert_services_into_existent_core(
                        core_id, identified_services)
                    yield f'Inserted services into Quickbase core'

                    # this part will send the data for a ticket formation and generate_tickets_zendesk in case we have services affected

                    if services is not None:
                        tickets, errors = generate_tickets_zendesk(
                            identified_services,
                            common_fields['start_date'], common_fields['end_date'],
                            common_fields['downtime'],  common_fields['location'],
                            description=common_fields['Description_to_customers'],
                            prefixes_and_contacts=prefixes_and_contacts, core_id=core_id)

                        yield f'Generated tickets in Zendesk: {tickets}'
                        yield f'Errors to open tickets in Zendesk: {errors}'

                        if tickets:
                            formulario.tickets_zendesk_generated = tickets
                            formulario.save()
                            email = EmailNotification()
                            email.send_notification(
                                core_id=core_id, tickets=tickets, date=common_fields['start_date'])

                            kwargs = {
                                'get_services_affecteds': common_fields['affected_services'],
                                'start_date': common_fields['start_date'],
                                'end_date':  common_fields['end_date'],
                                'element': [[pop_name[0][0]]]
                            }
                            CreateCalendarEvent(**kwargs)

                            yield f'Created event in Google Calendar'

                            zabbix_maintenance_id = None

                            zabbix_maintenance_id = create_zabbix_maintenance(services=identified_services,
                                                                              start_maintenance=common_fields[
                                                                                  'start_date'],
                                                                              end_maintenance=common_fields['end_date'],
                                                                              core_id=core_id)

                            formulario.zabbix_maintenance_id = zabbix_maintenance_id
                            formulario.save()
                            yield f'Created maintenance window in Zabbix for the services'

                    else:
                        return 'No identified services to include'
                return 'No services to create tickets or zabbix maintenances'
            else:
                yield 'Error to open core'
                return None
