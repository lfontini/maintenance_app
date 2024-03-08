import requests
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os

# load enviroments variables
load_dotenv()
HOSTNAME_QB = os.environ.get("HOSTNAME_QB")
TOKEN_QB = os.environ.get("TOKEN_QB")


def insert_service(info, core_id):

    ''' This function receive the service information as id and the core id and insert into 
    the core id in quickbase 
    
    '''
    print("inserinfo", info, core_id)
    id = info['id']
    status = info['status']
    if status == "Delivered":
        print(f"Inserting service {id} into core {core_id}")
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
        print(response)
        if response.status_code == 200:
            print(f'Service {id} inserted into core {core_id}')
        else:
            print(
                f"Failed to insert service {id} into core {core_id}. Status code: {response.status_code}")
    else:
        print(f"Service {id} is not delivered. STATUS: {status}")


def insert_services_into_existent_core(core_id, service_data):

    ''' This function receive the services from front-end and call for a function to
    include these services into the core in quickbase
    '''
    print(service_data)
    for _, services in service_data['attributes'].items():
        insert_service(services, core_id)
