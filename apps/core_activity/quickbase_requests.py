import requests
from dotenv import load_dotenv
import os
import time
import json
# Load vars from  .env file
load_dotenv()
HOSTNAME_QB = os.environ.get("HOSTNAME_QB")
TOKEN_QB = os.environ.get("TOKEN_QB")

headers = {
    'QB-Realm-Hostname': HOSTNAME_QB,
    'User-Agent': '{User-Agent}',
    'Authorization': TOKEN_QB
}


def fetch_activity_data(database, fields, where):
    url = "https://api.quickbase.com/v1/records/query"
    params = {
        "from": database,
        "select": fields,
        "where": where
    }

    response = requests.post(url, headers=headers, json=params)

    if response.status_code == 200:
        data = response.json()
        values = []
        for field in fields:
            values.append([record[f'{field}']["value"]
                          for record in data["data"]])
        return values
    else:
        print(f"Failed to fetch data. Status Code: {response.status_code}")
        return None


def get_paths_from_quickbase(netword_id):
    '''
        This function receive the network link id from front end and retrive paths from quickbase record 

    '''

    body = {
        "from": "bmh9sizyd",
        "select": [],
        "where": "{9.CT." + f"'{netword_id}'"+"} AND {42.CT.'Active'}"}
    # body = {"from":"bmh9sizyd","select":[],"where":"{9.CT.'FOR1-BEL2-01'}AND{42.CT.'Active'}"}

    r = requests.post(
        'https://api.quickbase.com/v1/records/query',
        headers=headers,
        json=body
    )
    result = r.json()

    paths = []
    for field in result['data']:
        if field['7']['value'] is not paths:
            paths.append(field['7']['value'])

    return paths

# print(json.dumps(r.json(),indent=4))


# com base no path ele retorna os servicos associados
def get_serves_from_paths(path):
    '''

    This function receive path id and return services attached to this path recorded in quickbase 

    '''

    attempts = 1
    waitfor = 1

    while attempts <= 3:
        time.sleep(waitfor)

        # Function that returns services associated with a given path
        body = {"from": "bfwgbisz4", "select": [
            7, 36, 409, 410, 334, 335], "where": "{'36'.EX.'delivered'}AND{335.CT." + f"'{path}'" + "}", "sortBy": [{"fieldId": 335, "order": "ASC"}]}

        r = requests.post(
            'https://api.quickbase.com/v1/records/query',
            headers=headers,  # Make sure you have defined this variable in your code
            json=body
        )

        if r.status_code == 200:
            result = r.json()
            services = []
            for field in result['data']:
                if field['7']['value'] not in services:
                    services.append(field['7']['value'])

            data = {'services': services}
            return data
        else:
            print(f"Attempt {attempts} failed. Status code: {r.status_code}")
            attempts += 1
            waitfor *= 2

    print("All attempts failed. Exiting.")
    return None


def Get_service_info(service_id):
    print("testando ... ", service_id)
    attempts = 1
    waitfor = 3
    while attempts <= 3:
        time.sleep(waitfor)
        print("waiting for ", waitfor)

        body = {"from": "bfwgbisz4", "select": [
            465, 467, 337, 36, 25, 3,  511, 700], "where": "{7.CT." + f"'{service_id}'" + "}"}

        r = requests.post(
            'https://api.quickbase.com/v1/records/query',
            headers=headers,
            json=body
        )
        print("response ", r.json(), r.status_code)
        if r.status_code == 200:
            result = r.json()
            if result['data']:
                for field in result['data']:
                    id = field['3']['value']
                    address = field['25']['value']
                    end_customer = field['337']['value']
                    city = field['465']['value']
                    country = field['467']['value']
                    status = field['36']['value']
                    diversity = field['511']['value']
                    related_diverse_service = field['700']['value']
                return {'id': id, 'address': address, 'end_customer': end_customer, 'city': city, 'country': country, 'status': status, 'diversity': diversity, 'related_diverse_service': related_diverse_service}
            else:
                print("None data retrived")
                return None
        else:
            print(
                f"Attempts {attempts} failed. status code: {r.status_code}")
            attempts += 1
            waitfor *= 2
        print("passando aqui ")
    print("Function Get_service_info failed to get data from qb")
    return None


def get_customers_contact(customer_prefix, max_retries=3):
    ''' 
    This function retrive customer contact zendesk_id from quickbase 

    input = prefix like VZB 
    return tuple ('379552854711,372976258952,398233342191,399117128812,382040915711,389565427611', 'Embratel')

    '''

    body = {"from": "bgvi3a68b", "select": [
        20, 64, 65, 64, 69, 70, 17, 55],
        "where": "{65.CT." + f"'{customer_prefix}'"+"}OR{70.CT." + f"'{customer_prefix}'"+"}OR{7.CT." + f"'{customer_prefix}'"+"}AND{55.CT.'NOC'} "}

    attempt = 1
    while attempt <= max_retries:
        try:
            r = requests.post(
                'https://api.quickbase.com/v1/records/query',
                headers=headers,
                json=body
            )

            if r.status_code == 200:
                response = r.json()
                if 'data' in response and response['data']:
                    request_ids_zendesk = response['data'][0]['69']['value']
                    customer_name = response['data'][0]['20']['value']
                    return request_ids_zendesk, customer_name
                else:
                    return None
            # In case of failure, print error details
            print(f'Attempt {attempt} failed to fetch customer data')
            print(f'Status code: {r.status_code}')
            print(f'Response text: {r.text}')
            attempt += 1

        except requests.exceptions.ConnectionError as e:
            # Capture the connection error exception
            print(f'Connection error: {e}')

            if attempt < max_retries:
                # Wait before retrying
                wait_time = 3 ** attempt
                print(f'Waiting {wait_time} seconds before retrying...')
                time.sleep(wait_time)

            attempt += 1

    print(f'Maximum number of attempts reached. Failed to fetch customer data.')
    return None, None


def get_services_from_nni(nni):
    '''

    This function will return a list of services from a nni

    '''
    try:
        headers = {
            'QB-Realm-Hostname': HOSTNAME_QB,
            'User-Agent': '{User-Agent}',
            'Authorization': TOKEN_QB
        }

        body = {
            "from": "bmeeuqk9d",
            "select": [7],
            "where": "{21.CT.'%s'}AND{18.CT.'Delivered'}" % nni
        }

        url = 'https://api.quickbase.com/v1/records/query'
        r = requests.post(url, headers=headers, json=body)

        # Verifica o código de status da resposta
        r.raise_for_status()

        response_json = r.json()

        # Verifica se o campo "data" está vazio
        if not response_json['data']:
            return None
        else:
            # Extrai os valores dos serviços e coloca em uma lista
            services_list = [record['7']['value']
                             for record in response_json['data']]
            return services_list
    except requests.exceptions.RequestException as e:
        print("Erro de requisição:", e)
        return None
    except json.JSONDecodeError as e:
        print("Erro ao decodificar JSON:", e)
        return None
    except KeyError as e:
        print("Chave não encontrada:", e)
        return None
    except Exception as e:
        print("Ocorreu um erro inesperado:", e)
        return None
