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
import concurrent.futures
import multiprocessing
import logging
from datetime import datetime, timedelta

# Configure the logging system
logging.basicConfig(filename='error_log.txt', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')


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
        <br>
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
                <td>Scheduled maintenance window to enhance network performance and reliability, ensuring a better quality to our customers</td>
            </tr>
            <tr>
                <td>Description </td>
                <td>{{ description }}</td>
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
                             "public": True, }
        ticket["subject"] = "Planned work" + data['start_date']
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


def prepare_tickets_worker(args):
    services_raw, start_date, end_date, down_time, location, description = args
    services = ' '.join(services_raw)  # Converte a lista para uma string
    services_raw_not_categorized = re.findall(
        r'[a-zA-Z0-9]{3}\.[0-9]{3,5}\.[a-zA-Z][0-9]{3}', services_raw)
    errors = []
    tickets = []
    services = set(services_raw_not_categorized)
    customers = {}

    for circuit in services:
        customer_prefix = circuit.split(".")[0]
        if customer_prefix not in customers:
            customers[customer_prefix] = []
        customers[customer_prefix].append(circuit)

    print('customers', customers)

    for customer in customers.keys():
        service = customers[customer][0]
        services = customers[customer]
        print('customers')
        customer_raw_data = get_customers_contact(customer)
        if customer_raw_data:
            contact_list, customer_name = get_customers_contact(customer)
            requester_id = contact_list[0]
            contact_copy = contact_list
            customer_info = Get_service_info(customers[customer][0])
            id = customer_info['id']
            address = customer_info['address']
            end_customer = customer_info['end_customer']
            city = customer_info['city']
            country = customer_info['country']

            context = {
                'customer_name': customer_name,
                'start_date': start_date,
                'end_date': end_date,
                'downtime': down_time,
                'location': location,
                'services': services,
                'description': description,
            }

            ventana_body = generate_notification_template(context)

            data = {
                "requester_id": requester_id,
                "cc": contact_copy,
                "end_date": end_date,
                "start_date": start_date,
                "city": city,
                "country": country,
                "service": service,
                "end_customer": end_customer,
                "body": ventana_body
            }

            tickets.append(Mount_tickets(data))
        else:
            logging.error(
                f'the customer {customer} is not registreted in quickbase')
            errors.append(
                f'the customer {customer} is not registreted in quickbase the service of this specific customer will not be open, but the other will create normally')
    return tickets, errors


def prepare_tickets(services_raw, start_date, end_date, down_time, location, description):
    # Convert services_raw to a string
    services = ' '.join(services_raw.split())

    # Use ThreadPoolExecutor for parallel processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Map the worker function to the chunks
        results = list(executor.map(prepare_tickets_worker, [
            (services, start_date, end_date, down_time, location, description)]))

    # Initialize lists to store tickets and errors
    tickets = []
    all_errors = []

    # Iterate over results to access tickets and errors
    for result in results:
        result_tickets, errors = result
        tickets.extend(result_tickets)  # Add tickets to the list
        if errors:
            all_errors.extend(errors)  # Add errors to the list

    return tickets, all_errors


def create_tickets(data_tickets):
    payload = {"tickets": data_tickets}

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
    ''' This function formats the date from Zendesk standard and adds 3 hours'''

    current_data_format = date

    entry_format_date = "%Y-%m-%dT%H:%M"

    # Zendesk format
    zendesk_format = "%d/%m/%Y %H:%M"

    try:
        # Convert the input date string to a datetime object
        converted_date = datetime.strptime(
            current_data_format, entry_format_date)

        # Add 3 hours to the converted date
        adjusted_date = converted_date + timedelta(hours=3)

        # Format the adjusted date in Zendesk format
        formated_date = adjusted_date.strftime(zendesk_format)

        return formated_date
    except ValueError as e:
        print(f"Error parsing date: {e}")
        return None


def generate_tickets_zendesk(services, start_date, end_date, down_time, location, description):
    start_date_zendesk_format = Ajust_date(start_date)
    end_date_zendesk_format = Ajust_date(end_date)
    data_tickets, all_errors = prepare_tickets(services_raw=services, start_date=start_date_zendesk_format,
                                               end_date=end_date_zendesk_format, down_time=down_time, location=location, description=description)
    ticket_numbers = create_tickets(data_tickets)
    return ticket_numbers, all_errors
