import requests

headers = {
    'QB-Realm-Hostname': 'ignetworks.quickbase.com',
    'User-Agent': '{User-Agent}',
    'Authorization': 'QB-USER-TOKEN b77d3x_w4i_0_b5vmciccskkpez3b6bnwbum2vpz'
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
    print("nl ", netword_id)
    body = {
        "from": "bmh9sizyd",
        "select": [],
        "where": "{9.CT." + f"'{netword_id}'"+"} AND {42.CT.'Active'}"}
    # body = {"from":"bmh9sizyd","select":[],"where":"{9.CT.'FOR1-BEL2-01'}AND{42.CT.'Active'}"}

    print("AAAAAAAAAAAAAAA PATH", body)
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
    body = {"from": "bfwgbisz4", "select": [
        7, 36, 409, 410, 334, 335], "where": "{'36'.EX.'delivered'}AND{335.CT." + f"'{path}'"+"}", "sortBy": [{"fieldId": 335, "order": "ASC"}]}
    # abaixo o que funciona
    # body = {"from":"bfwgbisz4","select":[7,36,409,410,334,335],"where":"{'36'.EX.'delivered'}AND{'335'.CT.'BOG1-MIA1-DFW1&NYC1'}","sortBy":[{"fieldId":335,"order":"ASC"}]}
    r = requests.post(
        'https://api.quickbase.com/v1/records/query',
        headers=headers,
        json=body
    )

    result = r.json()
    services = []
    for field in result['data']:
        if field['7']['value'] is not services:
            services.append(field['7']['value'])

    data = {'services': services}

    return data


def Get_service_info(service_id):
    '''

    That Function receive the service_id and return quickbase id and service id

    '''

    body = {"from": "bfwgbisz4", "select": [465, 467, 337, 25,
                                            3], "where": "{7.CT." + f"'{service_id}'"+"}"}

    r = requests.post(
        'https://api.quickbase.com/v1/records/query',
        headers=headers,
        json=body
    )
    result = r.json()
    if result['data']:
        for field in result['data']:
            id = field['3']['value']
            address = field['25']['value']
            end_customer = field['337']['value']
            city = field['465']['value']
            country = field['467']['value']

    return {'id': id, 'address': address, 'end_customer': end_customer, 'city': city, 'country': country}
