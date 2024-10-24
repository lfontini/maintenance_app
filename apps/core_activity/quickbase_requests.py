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


def fetch_activity_data(database, fields, where, sortby):
    url = "https://api.quickbase.com/v1/records/query"
    params = {
        "from": database,
        "select": fields,
        "where": where,
        "sortBy": sortby
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
