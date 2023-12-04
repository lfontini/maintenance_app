
import json
import requests
from dotenv import load_dotenv
import os
# Load vars from  .env file
load_dotenv()
HOSTNAME_QB = os.environ.get("HOSTNAME_QB")
TOKEN_QB = os.environ.get("TOKEN_QB")


def get_customers_contact(customer_prefix):
    headers = {
        'QB-Realm-Hostname': HOSTNAME_QB,
        'User-Agent': '{User-Agent}',
        'Authorization': TOKEN_QB
    }
    body = {"from": "bgvi3a68b", "select": [
        20, 64, 65, 64, 69, 70, 17, 55],
        "where": "{65.CT." + f"'{customer_prefix}'"+"}OR{70.CT." + f"'{customer_prefix}'"+"}AND{55.CT.'NOC'} "}
    r = requests.post(
        'https://api.quickbase.com/v1/records/query',
        headers=headers,
        json=body
    )

    if r.status_code == 200:
        response = r.json()
        if 'data' in response:
            if response['data']:
                request_ids_zendesk = response['data'][0]['69']['value']
                customer_name = response['data'][0]['20']['value']

                return request_ids_zendesk, customer_name
    else:
        print('Erro ao buscar dados do cliente')
        print(r.status_code)
        print(r.text)
        return None, None
