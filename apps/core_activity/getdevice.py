import re
import requests
import os
from dotenv import load_dotenv

# Load vars from  .env file
load_dotenv()
TOKEN_NETBOX = os.environ.get("TOKEN_NETBOX")
HOSTNAME_QB = os.environ.get("HOSTNAME_QB")
TOKEN_QB = os.environ.get("TOKEN_QB")
URL_NETBOX = os.environ.get("URL_NETBOX")
print(URL_NETBOX)


def Get_Device_Data_From_Quickbase(circuito):
    '''

This function will get the device data from Quickbase 
and return a dict ex {'manufacturer': 'MikroTik', 'ip': '172.23.43.234', 'model': 'HEX-S'}

    '''
    headers = {
        'QB-Realm-Hostname': HOSTNAME_QB,
        'User-Agent': '{User-Agent}',
        'Authorization': TOKEN_QB
    }

    body = {"from": "bjj6j8a3g",
            "select": [25, 166, 177],
            "where": "{47.CT." + f"'{circuito}'"+"}OR{60.CT." + f"'{circuito}'"+"}"
            }

    r = requests.post(
        'https://api.quickbase.com/v1/records/query',
        headers=headers,
        json=body
    )

    a = r.json()
    print(a)
    data = {}
    if a['data']:
        for item in a['data']:
            data["manufacturer"] = item['177']['value']
            data["ip"] = item['25']['value']
        return data
    data["manufacturer"] = 'none'
    data["ip"] = 'none'
    return data


def Get_Device_Data(device_name):
    '''
    This function will get the device data from Netbox

    and return a dict ex 

    --- {'manufacturer': 'MikroTik', 'ip': '172.23.43.234', 'model': 'HEX-S'}

    '''

    print("CHEKING IN NETBOX... ", device_name)
    Patter_ipv4 = "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"

    device_name = device_name

    data = {'manufacturer': 'none', 'ip': 'none'}

    url = f"{URL_NETBOX}/api/dcim/devices/?q={device_name}"

    payload = {}

    headers = {
        'Content-Type': 'application/json ',
        'Authorization': f'token  {TOKEN_NETBOX}'}

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        resposta_json = response.json()
        results = resposta_json["results"]

        if results:
            for info in results:
                manufacturer = info['device_type']['manufacturer']['display']
                if manufacturer.lower() == 'cisco' or manufacturer.lower() == 'mikrotik' or manufacturer.lower() == 'accedian':
                    if info['primary_ip']:
                        if 'address' in info['primary_ip'] and info['primary_ip'] != None:
                            # prefix = ex 192.168.1.1/24
                            prefix = info['primary_ip']['address']

                        modelo = info['device_type']['model']

                        if prefix != 'none':
                            # Select ip
                            ip = re.findall(Patter_ipv4, prefix)
                            data['manufacturer'] = manufacturer
                            data['ip'] = ip[0]
                            data['model'] = modelo

        return data
    except requests.exceptions.ConnectionError as e:
        print(
            f"error to access data from netbox ERROR please check the connection {e}")
        return None
