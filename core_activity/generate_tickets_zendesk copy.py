from jinja2 import Template
from .get_contacts_from_quickbase import get_customers_contact
from .quickbase_requests import Get_service_info
import json
import re
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
import os

# load enviroments variables
load_dotenv()
ZENDESK_URL = os.environ.get("ZENDESK_URL")
TOKEN_ZD = os.environ.get("TOKEN_ZD")

url = ZENDESK_URL+"/api/v2/tickets/create_many"

headers = {
    # Replace 'YOUR_API_KEY' with your actual API key
    'Authorization': TOKEN_ZD,
    'Content-Type': 'application/json'  # Fixed the content-type header
}


def generate_notification_template(context):
    # Defina o template HTML
    template_string = """
<!DOCTYPE html>
<html>

<head>
    <style>



        .title {
            text-align: justify;
        }

        body {
            background-color: #3498db;
            font-family: Arial, sans-serif;
        }

        .container {
            width: 80%;
            max-width: 1000px;
            background-color: #fff;
            margin: 0 auto;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
        }

        .header {
            text-align: justify;
        }

        table {
            width: 100%;
        }

        table,
        th,
        td {
            border: 1px solid #333;
            border-collapse: collapse;
        }

        th,
        td {
            padding: 10px;
            text-align: left;
        }

        th {
            background-color: #3498db;
            color: #fff;
        }

        img {
            width: 100px;
            float: right;
            margin-right: 20px;
        }
    </style>
</head>

<body>
    <div class="container">
        <div class="header">
            <img src="https://static.wixstatic.com/media/7e4e6f_29d3996755c4460ab5fed99424c9db85~mv2.png/v1/crop/x_57,y_221,w_1446,h_369/fill/w_255,h_65,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/Logotipo%20IG_Mesa%20de%20trabajo%201.png" alt="Logo">
            <h2>Maintenance Activities Notification</h2>
            <p> Dear Team {{ customer_name }}  </p>
            <p class="title">This ticket is to notify you of maintenance activities we will be performing on our network
                which will affect your service with sporadic flaps or outage for the following period of time.</p>
        </div>
        <table>
            <tr>
                <th>Description</th>
                <th>Details</th>
            </tr>
            <tr>
                <td>Starting Date/Time</td>
                <td>{{ start_date }} UTC</td>
            </tr>
            <tr>
                <td>Finalizing Date/Time</td>
                <td>{{ end_date }} UTC</td>
            </tr>
            <tr>
                <td>Estimated Downtime</td>
                <td>{{ downtime }} </td>
            </tr>
            <tr>
                <td>Activity</td>
                <td>Maintenance Window to improve network</td>
            </tr>
            <tr>
                <td>Location</td>
                <td>{{ location }}</td>
            </tr>
            <tr>
                <td>Affected Service(s)</td>
                <td>
                    {% for service in services %}
                        {{ service }}<br>
                    {% endfor %}
                </td>
            </tr>
        </table>
        <div>
            <p>If we do not receive any response regarding the activity we will consider it as accepted</p>
        </div>
    </div>
</body>

</html>

    """

    template = Template(template_string)

    output = template.render(context)

    return output


def Mount_tickets(data):
    ticket = {}  # Define ticket as a dictionary
    if data:
        ticket["comment"] = {"html_body": data['body'],
                             "public": False, }
        ticket["subject"] = "Planed work " + data['start_date']
        ticket["assignee_id"] = 16632994687
        ticket["status"] = "pending"
        ticket["priority"] = 'normal'
        ticket["requester_id"] = data['requester_id']
        ticket["submitter_id"] = 16632994687
        ticket["organization_id"] = 14099514728
        ticket["collaborator_ids"] = [1266469881070]
        ticket["tags"] = ["a", "maintenance_window"]
        ticket["custom_fields"] = [
            {"id": 48746547, "value": "maintenance_window"},
            {'id': 49079068, 'value': data['end_date']},
            {'id': 360026351931, 'value': False},
            {'id': 48751787, 'value': data['start_date']},
            {'id': 114096793931, 'value': data['city']},
            {'id': 360006391391, 'value': False},
            {'id': 360006391411, 'value': False},
            {'id': 114096793771, 'value': data['country']},
            {'id': 45713588, 'value': data['service']},
            {'id': 114100679152, 'value': data['end_customer']},
        ]
        ticket["fields"] = [
            {'id': 49079068, 'value': data['end_date']},
            {'id': 48751787, 'value': data['start_date']},
            {"id": 48746547, "value": "maintenance_window"},
            {'id': 360026351931, 'value': False},
            {'id': 114096793931, 'value': data['city']},
            {'id': 360006391391, 'value': False},
            {'id': 360006391411, 'value': False},
            {'id': 49441688, 'value': False},
            {'id': 114096793771, 'value': data['country']},
            {'id': 45713588, 'value': data['service']},
            {'id': 114100679152, 'value': data['end_customer']},
        ]
        ticket["ticket_form_id"] = 412287
        ticket["brand_id"] = 2791727

        return ticket


def prepare_tickets(services, start_date, end_date, down_time, location):
    '''

    This functon will get the raw services and separe properly per customer prefix ex VZB EMB etc
    and mount the ticket and return to be generated by generate function 

    '''
    services_raw = re.findall(
        r'[a-zA-Z0-9]{3}\.[0-9]{3,5}\.[a-zA-Z][0-9]{3}', services)
    print(services_raw)
    tickets = []
    services = set(services_raw)
    customers = {}
    for circuit in services:
        customer_prefix = circuit.split(".")[0]
        if customer_prefix not in customers:
            customers[customer_prefix] = []
        customers[customer_prefix].append(circuit)

    for customer in customers.keys():
        service = customers[customer][0]
        services = customers[customer]
        contact_list, customer_name = get_customers_contact(customer)
        requester_id = contact_list[0]
        customer_info = Get_service_info(customers[customer][0])
        print('contact_list', contact_list)
        id = customer_info['id']
        address = customer_info['address']
        end_customer = customer_info['end_customer']
        city = customer_info['city']
        country = customer_info['country']

        context = {
            'customer_name': customer_name,
            'start_date': start_date,
            'end_date':  end_date,
            'downtime': down_time,
            'location': location,
            'services': services,
        }

        ventana_body = generate_notification_template(context)

        data = {
            "requester_id": 1266469881070,
            "cc": 'cc',
            "end_date": end_date,
            "start_date": start_date,
            "city": city,
            "country": country,
            "service": service,
            "end_customer": end_customer,
            "body": ventana_body
        }

        tickets.append(Mount_tickets(data))
    return tickets


def create_tickets(data_tickets):
    payload = {"tickets": data_tickets}

    print(json.dumps(payload, indent=4))

    # Used requests.post instead of requests.request
    response = requests.post(url, headers=headers, json=payload)
    status_request = response.json()['job_status']['status']
    request_url = response.json()['job_status']['url']
    if True:
        if response.ok:
            while (status_request != "completed"):
                response1 = requests.get(request_url, headers=headers)
                status_request = response1.json()['job_status']['status']
                time.sleep(1)
            if status_request == "completed":
                ticket_ids = ','.join(
                    [str(item['id']) for item in response1.json()['job_status']['results']])

            return ticket_ids


def Ajust_date(date):
    '''     This funtion format the date from zendesk stardart   '''

    current_data_format = date

    entry_format_date = "%Y-%m-%dT%H:%M"

    # zendesk format
    zendesk_format = "%d/%m/%Y %H:%M"

    # converted date
    converted_date = datetime.strptime(current_data_format, entry_format_date)

    # wished format
    formated_date = converted_date.strftime(zendesk_format)

    return formated_date


def generate_tickets_zendesk(services, start_date, end_date, down_time, location):
    ''' this function receive the services and generate tickets 
    from each group of customers and 
    return tickets number '''

    start_date_zendesk_format = Ajust_date(start_date)
    end_date_zendesk_format = Ajust_date(end_date)

    data_tickets = prepare_tickets(services=services, start_date=start_date_zendesk_format,
                                   end_date=end_date_zendesk_format, down_time=down_time, location=location)
    ticket_numbers = create_tickets(data_tickets)
    return ticket_numbers
