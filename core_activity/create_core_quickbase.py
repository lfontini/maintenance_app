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
from .quickbase_requests import fetch_activity_data

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


def Insert_services_into_existent_core(core_id, services_raw):
    services = re.findall(
        r'[a-zA-Z0-9]{3}\.[0-9]{3,5}\.[a-zA-Z][0-9]{3}', services_raw)

    headers = {
        'QB-Realm-Hostname': HOSTNAME_QB,
        'User-Agent': '{User-Agent}',
        'Authorization': TOKEN_QB
    }

    def process_service(service):
        print("service", service)
        service_info = Get_service_info(service)
        print(service_info)
        id = service_info.get('id')
        print(id)
        if id:
            body = {"to": "bmniuvke2", "data": [{"8": {"value": id}, "10": {"value": core_id}}],
                    "fieldsToReturn": [10, 9]}
            response = requests.post(
                'https://api.quickbase.com/v1/records', headers=headers, json=body).json()

            return f'Service included successfully: {service}' if response.get('code') == 0 else None

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(filter(None, executor.map(process_service, services)))

    return results


def Ajust_Core_date(date):
    ''' 

        This function receive a date and return a new date 

    '''
    currunt_date = datetime.strptime(date, "%Y-%m-%dT%H:%M")
    new_date_formatted = currunt_date.strftime("%Y-%m-%dT%H:%M:%S")

    return new_date_formatted


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
    print('dadps recebidos ', data)
    '''
    This function receives data from the front end, validates it, and creates a core on Quickbase, returning the core number.
    '''

    activity_type = data.get('activity_type')
    activity_related_to = data.get('activity_related_to')

    common_fields = {
        'ign_engineer': data.get('ign_engineer'),
        'internet_id': data.get('internet_id'),
        'status': data.get('status'),
        'start_date': data.get('start_date'),
        'end_date': data.get('end_date'),
        'duration': data.get('duration'),
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
            new_date_formatted = Ajust_Core_date(common_fields['start_date'])
            duration_activity = Calc_duration_time_core(
                common_fields['start_date'], common_fields['end_date'])
            ign_engineer = data.get('ign_engineer')

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
            core_id = Make_quickbase_request(core_data)
            if core_id:
                if common_fields['affected_services']:
                    services = Insert_services_into_existent_core(
                        core_id, common_fields['affected_services'])
                    tickets, errors = generate_tickets_zendesk(common_fields['affected_services'],
                                                               common_fields['start_date'], common_fields['end_date'],
                                                               common_fields['duration'], common_fields['location'], description=common_fields['Description_to_customers'])
                    if tickets:
                        email = EmailNotification()
                        email.send_notification(
                            core_id=core_id, tickets=tickets, date=common_fields['start_date'])

                        description_calendar = f''' 
                        Test Automation Event will affect services \n
                        {common_fields['affected_services']}

                        '''
                        print(common_fields['start_date'],
                              common_fields['end_date'])
                        formated_start_data = Ajust_Core_date(
                            common_fields['start_date'])
                        formated_end_data = Ajust_Core_date(
                            common_fields['end_date'])

                        event_creator = EventCreator(calendar_title=f'Planned Work Maintenance DIA {internet_name[0][0]}',
                                                     start_time=formated_start_data,
                                                     end_time=formated_end_data,
                                                     description=description_calendar)
                        event_creator.create_event()

                        return {'core_id': core_id, 'tickets': tickets,  'errors': errors}
                else:
                    return None
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
            core_id = Make_quickbase_request(core_data)
            if core_id:
                if common_fields['affected_services']:
                    services = Insert_services_into_existent_core(
                        core_id, common_fields['affected_services'])
                    tickets, errors = generate_tickets_zendesk(common_fields['affected_services'],
                                                               common_fields['start_date'], common_fields['end_date'],
                                                               common_fields['duration'], common_fields['location'], description=common_fields['Description_to_customers'])
                    if tickets:
                        email = EmailNotification()
                        email.send_notification(
                            core_id=core_id, tickets=tickets, date=common_fields['start_date'])

                        description_calendar = f''' 
                        Test Automation Event will affect services \n
                        {common_fields['affected_services']}

                        '''
                        print(common_fields['start_date'],
                              common_fields['end_date'])
                        formated_start_data = Ajust_Core_date(
                            common_fields['start_date'])
                        formated_end_data = Ajust_Core_date(
                            common_fields['end_date'])

                        event_creator = EventCreator(calendar_title=f'Planned Work Maintenance Network Link {network_link_name[0][0]}',
                                                     start_time=formated_start_data,
                                                     end_time=formated_end_data,
                                                     description=description_calendar)
                        event_creator.create_event()

                        return {'core_id': core_id, 'tickets': tickets, 'errors': errors}
                else:
                    return None
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
            core_id = Make_quickbase_request(core_data)
            if core_id:
                if common_fields['affected_services']:
                    services = Insert_services_into_existent_core(
                        core_id, common_fields['affected_services'])
                    tickets, errors = generate_tickets_zendesk(common_fields['affected_services'],
                                                               common_fields['start_date'], common_fields['end_date'],
                                                               common_fields['duration'], common_fields['location'], description=common_fields['Description_to_customers'])
                    if tickets:
                        email = EmailNotification()
                        email.send_notification(
                            core_id=core_id, tickets=tickets, date=common_fields['start_date'])

                        description_calendar = f'''A core maintenance will be perform \n
                        <H1>Services that will be affected </H1>
                        {common_fields['affected_services']}

                        '''
                        print(common_fields['start_date'],
                              common_fields['end_date'])
                        formated_start_data = Ajust_Core_date(
                            common_fields['start_date'])
                        formated_end_data = Ajust_Core_date(
                            common_fields['end_date'])

                        event_creator = EventCreator(calendar_title=f'Planned Work Maintenance POP {pop_name[0][0]}',
                                                     start_time=formated_start_data,
                                                     end_time=formated_end_data,
                                                     description=description_calendar)
                        event_creator.create_event()

                        return {'core_id': core_id, 'tickets': tickets, 'errors': errors}
                else:
                    return None
            return None

    return None
