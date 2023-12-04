import requests
import json

url = "https://ignetworks.zendesk.com/api/v2/tickets.json"  # Corrected the URL

payload = {
    "ticket": {
        "comment": {
            "body": "Window maintenance test FONTINI"
        },
        "priority": "normal",
        "subject": "Maintenance example",  # Fixed the typo in "example"
        "assignee_id": 16632994687,
        "status": "open",
        "requester_id": 1266469881070,
        "submitter_id": 16632994687,
        "organization_id": 14099514728,
        "collaborator_ids": [1266469881070],  # Corrected the list syntax
        "tags": ["a", "maintenance_window"],
        "custom_fields": [
            {"id": 48746547, "value": "maintenance_window"},
            {'id': 49079068, 'value': '01/01/2022 10:01'},
            {'id': 360026351931, 'value': False},
            {'id': 48751787, 'value': '01/01/2022 10:00'},
            {'id': 114096793931, 'value': 'ZCITY'},
            {'id': 360006391391, 'value': False},
            {'id': 360006391411, 'value': False},
            {'id': 114096793771, 'value': 'COUNTRY'},
            {'id': 45713588, 'value': "FON.5555.D001"},
            {'id': 114100679152, 'value': 'CLIENTE FINAL EXEMPLO '},

        ],
        'fields': [
            {'id': 49079068, 'value': '01/01/2022 10:01'},
            {'id': 48751787, 'value': '01/01/2022 10:00'},
            {"id": 48746547, "value": "maintenance_window"},
            {'id': 360026351931, 'value': False},
            {'id': 114096793931, 'value': 'ZCITY TEST'},
            {'id': 360006391391, 'value': False},
            {'id': 360006391411, 'value': False},
            {'id': 49441688, 'value': False},
            {'id': 114100679152, 'value': 'CLIENTE FINAL EXEMPLO '},


        ],
        'ticket_form_id': 412287,
        'brand_id': 2791727,
    }
}

headers = {
    # Replace 'YOUR_API_KEY' with your actual API key
    'Authorization': 'Basic bm9jQGlnbmV0d29ya3MuY29tL3Rva2VuOk8yUTdYeGZScUxJOHF2MEF1NGxtSk10NnVEOHhqTU1wdUlrUU96YUI=',
    'Content-Type': 'application/json'  # Fixed the content-type header
}

# Used requests.post instead of requests.request
response = requests.post(url, headers=headers, json=payload)

print(response.json())

url = "https://ignetworks.zendesk.com/api/v2/tickets/count"
headers = {
    "Content-Type": "application/json",
}

response = requests.request(
    "GET",
    url,
    auth=('lfontini@ignetworks.com  6atYijjC', '6atYijjC'),
    headers=headers
)

print(response.text)
