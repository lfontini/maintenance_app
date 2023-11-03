import requests
from datetime import datetime
import os
from dotenv import load_dotenv
from .quickbase_requests import Get_service_info
import re

# load enviroments variables
load_dotenv()
HOSTNAME_QB = os.environ.get("HOSTNAME_QB")
TOKEN_QB = os.environ.get("TOKEN_QB")


def Make_quickbase_request(data):
    print(data)
    headers = {
        'QB-Realm-Hostname': HOSTNAME_QB,
        'User-Agent': '{User-Agent}',
        'Authorization': f'QB-USER-TOKEN {TOKEN_QB}'
    }

    body = {"to": "bk32qj72c", "data": [data], "fieldsToReturn": [3]}
    r = requests.post(
        'https://api.quickbase.com/v1/records',
        headers=headers,
        json=body
    )

    if r.status_code == 200:
        response = r.json()
        if 'data' in response:
            if response['data']:
                for field in response['data']:
                    id = field['3']['value']
                    return id

    return r.status_code, r.json()


def Insert_services_into_existent_core(core_id, services_raw):
    services = re.findall(
        r'[a-zA-Z0-9]{3}\.[0-9]{3,5}\.[a-zA-Z][0-9]{3}', services_raw)

    headers = {
        'QB-Realm-Hostname': HOSTNAME_QB,
        'User-Agent': '{User-Agent}',
        'Authorization': f'QB-USER-TOKEN {TOKEN_QB}'
    }

    for service in services:
        service_info = Get_service_info(service[0])
        id = service_info['id']
        services_included_to_core = []
        print(service, id)
        if id:
            body = {"to": "bmniuvke2", "data": [
                {"8": {"value": id}, "10": {"value": core_id}}], "fieldsToReturn": [10, 9]}
            r = requests.post(
                'https://api.quickbase.com/v1/records',
                headers=headers,
                json=body
            )
            print(body)
            response = r.json()
            if r.status_code == 200:
                services_included_to_core.append(service)
    return f'services included successfully {services_included_to_core} {response}'


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
    print(data)
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
        'affected_services': data.get('affected_services'),
        'location': data.get('location'),
    }

    new_date_formatted = Ajust_Core_date(common_fields['start_date'])
    duration_activity = Calc_duration_time_core(
        common_fields['start_date'], common_fields['end_date'])
    remote_hands_information = data.get('remote_hands_information')

    if activity_type == 'from_ign':
        if activity_related_to == 'internet_service':
            internet_id = data.get('internet_id')
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
                SERVICES = Insert_services_into_existent_core(
                    core_id, common_fields['affected_services'])
            return core_id, SERVICES

        if activity_related_to == 'network_link':
            network_link = data.get('network_link')
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
                SERVICES = Insert_services_into_existent_core(
                    core_id, common_fields['affected_services'])
            return core_id, SERVICES

        if activity_related_to == 'pop':
            pop = data.get('pop')
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
                SERVICES = Insert_services_into_existent_core(
                    core_id, common_fields['affected_services'])
            return core_id, SERVICES

    return None
