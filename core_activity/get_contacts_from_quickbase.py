import json
import requests


def get_customers_contact(customer_prefix):
    headers = {
        'QB-Realm-Hostname': 'ignetworks.quickbase.com',
        'User-Agent': '{User-Agent}',
        'Authorization': 'QB-USER-TOKEN b2hjmh_w4i_b2ytd7mdi8jjrpdg8khp8cmwkm6n'
    }
    body = {"from": "bgvi3a68b", "select": [
        20, 64, 65, 64, 69, 70, 17, 55],
        "where": "{65.CT." + f"'{customer_prefix}'"+"}OR{70.CT." + f"'{customer_prefix}'"+"}AND{55.CT.'NOC'} "}
    r = requests.post(
        'https://api.quickbase.com/v1/records/query',
        headers=headers,
        json=body
    )

    response = r.json()
    if 'data' in response:
        if response['data']:
            request_ids_zendesk = response['data'][0]['69']['value']
            customer_name = response['data'][0]['20']['value']

            return request_ids_zendesk, customer_name
    else:
        return None
