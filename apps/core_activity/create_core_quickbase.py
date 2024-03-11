import requests
from datetime import datetime
import os
from dotenv import load_dotenv
from .quickbase_requests import fetch_activity_data
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
    form = CoreForm(data=data)
    core_data = data
    if form.is_valid():
        print("form valido ")
        activity_type = core_data.get('activity_type')
        activity_related_to = core_data.get('activity_related_to')

        common_fields = {
            'ign_engineer': core_data.get('ign_engineer'),
            'status': core_data.get('status'),
            'start_date': core_data.get('start_date'),
            'end_date': core_data.get('end_date'),
            'duration': core_data.get('duration'),
            'downtime': core_data.get('downtime'),
            'description': core_data.get('Description'),
            'description_to_customers': core_data.get('Description_to_customers'),
            'remote_hands_information': core_data.get('remote_hands_information'),
            'location': core_data.get('location'),
        }

        new_date_formatted = Ajust_Core_date(common_fields['start_date'])
        duration_activity = Calc_duration_time_core(
            common_fields['start_date'], common_fields['end_date'])
        remote_hands_information = core_data.get('remote_hands_information')

        if activity_type == 'from_ign' or activity_type == 'from_vendor':
            if activity_related_to == 'internet_service':
                internet_id = core_data.get('field_id_internet_id')

                internet_name = fetch_activity_data(database="bjx5t3hbx",
                                                    fields=[6],
                                                    where="{3.EX." + f"'{internet_id}'"+"}")

                new_date_formatted = Ajust_Core_date(
                    date=common_fields['start_date'])

                duration_activity = Calc_duration_time_core(start_date=common_fields['start_date'],
                                                            end_date=common_fields['end_date'])
                ign_engineer = data.get('ign_engineer')

                core_data = {
                    "6": {"value": new_date_formatted},
                    "8": {"value": common_fields['description']},
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
                # core_id = '2863'
                if core_id:
                    formulario = form.save(commit=False)
                    formulario.core_quickbase_id = core_id
                    formulario.save()
                    id = formulario.id
                    return {"core_id": core_id, "id": id}
                else:
                    return f"Error to open core {core_id}"

        if activity_related_to == 'network_link':
            network_link = data.get('network_link')
            network_link_name = fetch_activity_data(database="bjvepudtt", fields=[
                7], where="{3.EX." + f"'{network_link}'"+"}")

            new_date_formatted = Ajust_Core_date(common_fields['start_date'])
            duration_activity = Calc_duration_time_core(
                common_fields['start_date'], common_fields['end_date'])
            ign_engineer = data.get('ign_engineer')

            core_data = {
                "6": {"value": new_date_formatted},
                "8": {"value": common_fields['description']},
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
            # core_id = '2863'
            if core_id:
                formulario = form.save(commit=False)
                formulario.core_quickbase_id = core_id
                formulario.save()
                id = formulario.id
                return {"core_id": core_id, "id": id}
            else:
                return f"Error to open core {core_id}"

        if activity_related_to == 'pop':
            pop = data.get('pop')
            pop_name = fetch_activity_data(database="bjvepsjqq", fields=[
                8], where="{3.EX." + f"'{pop}'"+"}")
            print(pop_name)
            new_date_formatted = Ajust_Core_date(common_fields['start_date'])

            duration_activity = Calc_duration_time_core(
                start_date=common_fields['start_date'],
                end_date=common_fields['end_date']
            )

            ign_engineer = data.get('ign_engineer')

            core_data = {
                "6": {"value": new_date_formatted},
                "8": {"value": common_fields['description']},
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
            # core_id = '1010'
            if core_id:
                formulario = form.save(commit=False)
                formulario.core_quickbase_id = core_id
                formulario.save()
                id = formulario.id
                return {"core_id": core_id, "id": id}
            else:
                return f"Error to open core {core_id}"

    return None, f" This form is invalid, check the fields and try again {form.errors}"
