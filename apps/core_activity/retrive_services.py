import requests
import re
from dotenv import load_dotenv
import os

load_dotenv()

user = os.getenv('user')
password = os.getenv('password')
TOKEN_NETBOX = os.getenv('TOKEN_NETBOX')
NETBOX_URI = os.getenv('URL_NETBOX')



def list_all_devices_pop(host_pop):
    ''' 
    This Function receive host_pop name as SAO3, MIA1, and it will return all device core and access 
    routers and switches, this data will be used into the select in front end
    
    '''
    url = f"{NETBOX_URI}/api/dcim/devices/?q={host_pop}&status=active&role_id=11&role_id=12&role_id=13"
    payload = {}
    headers = {
        'Content-Type': 'application/json ',
        'Authorization': f'token  {TOKEN_NETBOX}'}

    response = requests.request("GET", url, headers=headers, data=payload)
    resposta_json = response.json()
    results = resposta_json["results"]

    devices = [] 
    for device in results:
        devices.append(device['name'])

    return devices


def Eliminate_Duplicated_Services(services_raw):
    '''
    This function receive a raw services and eliminate duplicated services
    '''
    services_raw = services_raw
    services_raw = services_raw.split(",")
    services_raw = list(dict.fromkeys(services_raw))
    services_raw = ",".join(services_raw)
    return services_raw


def Filter_services_by_category(get_services, host):
    '''

    This function receive and categorize per type of service and return a dict 

    1'''
    popname = host
    if "access_error" in get_services:
        result = {}
        return result
    else:

        all_services_raw = str(
            (re.findall(r'[a-zA-Z0-9]{3}\.[0-9]{3,5}\.[a-zA-Z][0-9]{3}', get_services)))
        all_services = Eliminate_Duplicated_Services(all_services_raw)
        return all_services


def Get_pops_gogs(device_name):
    '''
    This function receive pop device name and return the services configured in it using gogs repo backup 
    reading the repo  gogs.ignetworks.com/IG_Networks/POPs

    '''

    raw_file_url = f'https://{user}:{password}@gogs.ignetworks.com/IG_Networks/POPs/raw/main/{device_name}'
    
    try:
        response = requests.get(raw_file_url, verify=False)
        print("gogsss ", response)

        if response.status_code == 200:
            raw_data = response.text
            return Filter_services_by_category(raw_data, device_name)
        else:
            print(f"Erro: Response code is  {response.status_code}")
            return None
    except Exception as e:
        print("raw_file_url", raw_file_url)
        print("Error to access gogs, please check connection" , e)
        return None


def List_services(devices):
    '''
    This function receive a list of devices and return a list of services configured in the devices
    '''
    lista_devices_pop = devices
    validated_device_name = []
    raw_data = ",".join(
        lista_devices_pop)  # Join the list into a single string\
    devices = (re.findall(r'[a-zA-Z0-9]{4}-[ASWLSRLERCR]{2,3}[0-9]', raw_data))
    result = []

    for device in devices:
        print(device)
        result.append(Get_pops_gogs(device)
                      )

    return result[0]
