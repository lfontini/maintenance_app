from jinja2 import Template
import requests
from datetime import datetime
from dotenv import load_dotenv
import os
import logging
from datetime import datetime, timedelta
from .models import Core

# Configure the logging system
logging.basicConfig(filename='error_log.txt', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# load enviroments variables
load_dotenv()
ZENDESK_URL = os.environ.get("ZENDESK_URL")
TOKEN_ZD = os.environ.get("TOKEN_ZD")

url = ZENDESK_URL+"/api/v2/tickets"

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
            <br>
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
        <br>
            <p>If we do not receive any response regarding the activity we will consider it as accepted</p>
        </div>
    </div>
</body>

</html>

    """

    template = Template(template_string)

    output = template.render(context)

    return output


def update_tickets_and_affected_services_for_core(id, new_ticket_info, new_affected_services):
    """
    Update ticket information and affected services for a specific Core.

    Args:
        core_id (int): The ID of the Core to be updated.
        new_ticket_info (str): The new ticket information to be added.
        new_affected_services (str): The new affected services to be updated.

    Returns:
        bool: True if the update is successful, False if the Core is not found.

    Raises:
        ValueError: If `core_id` is less than or equal to zero.
    """

    try:
        core = Core.objects.get(id=id)
        print("core ", core.tickets_zendesk_generated)
    except Core.DoesNotExist:
        # Core with the provided ID not found
        return False

    # Append or update the ticket information
    print("condicional if ", core.tickets_zendesk_generated)
    print("vars  ", new_ticket_info, new_affected_services)
    print("type  ", type(new_ticket_info), type(new_affected_services))

    if core.tickets_zendesk_generated:
        # If there are existing tickets, append the new ticket information
        core.tickets_zendesk_generated += ", " + new_ticket_info
        print("core cadastrado ", core.tickets_zendesk_generated)

    else:
        # If no existing tickets, set the new ticket information
        core.tickets_zendesk_generated = new_ticket_info

    # Update affected services
    core.affected_services += " ".join(new_affected_services) + " "

    # Save the changes
    core.save()

    # Return True if the update is successful
    return True


def Mount_tickets(data):
    ticket = {}  # Define ticket as a dictionary
    if data:
        ticket["comment"] = {"html_body": data['body'],
                             "public": True}
        ticket["subject"] = "Planned work " + data['start_date']
        ticket["assignee_id"] = 16632994687
        ticket["status"] = "open"
        ticket["priority"] = 'normal'
        ticket["requester_id"] = data['requester_id']
        ticket["submitter_id"] = 16632994687
        ticket["organization_id"] = 14099514728
        ticket["collaborator_ids"] = data['collaborator_ids']
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
    services_info, start_date, end_date, down_time, location, description, prefixes_and_contacts = args
    errors = []
    tickets = []
    customers = {}
    services_with_diversity = {}

    for service in services_info:
        if services_info[service]:
            print("service ", service)
            status = services_info[service].get('status', None)
            diversity = services_info[service].get('diversity', None)
            if status is not None and status == 'Delivered':
                customer_prefix = service.split(".")[0]
                if customer_prefix not in customers:
                    customers[customer_prefix] = []
                customers[customer_prefix].append(service)

            else:
                logging.error(
                    f'the service {service} is not Delivered in quickbase or it does not exist')
                errors.append(
                    f'the service {service} is not Delivered in quickbase')
            if diversity == 'Yes' and status == 'Delivered':
                related_diverse_service = services_info[service].get(
                    'related_diverse_service', None)
                print('related_diverse_service', related_diverse_service)
                if related_diverse_service is not None:
                    if service not in services_with_diversity.values():
                        services_with_diversity[service] = related_diverse_service
                    else:
                        print("vai remover o service", service,
                              customers[customer_prefix])
                        customers[customer_prefix].remove(service)
                        logging.error(
                            f'the service {service} has diversity with {related_diverse_service}')
                        errors.append(
                            f'the service {service} has diversity with {related_diverse_service}, ticket will not be generated')

    print('services_with_diversity', services_with_diversity)
    print('customers', customers)
    if customers:
        for customer in customers.keys():
            service = customers[customer][0]
            print('services', service)
            if service:
                print("entrou aqui ")
                services = customers[customer]
                customer_raw_data = prefixes_and_contacts.get(customer, None)
                if customer_raw_data:
                    contact_list, customer_name = customer_raw_data
                    # print('contact_list', contact_list)
                    # print('customer_name', customer_name)
                    # print('requester_id', contact_list.split(",")[0])
                    # print('contact_copy', contact_list.split(","))
                    requester_id = contact_list.split(",")[0]
                    contact_copy = [contact_list]
                    # requester_id = 1266469881070
                    # contact_copy = [21200390635547]
                    service = customers[customer][0]
                    service_info = services_info.get(service, None)

                    if service_info is not None:
                        id, address, end_customer, city, country = (
                            service_info.get('id'),
                            service_info.get('address'),
                            service_info.get('end_customer'),
                            service_info.get('city'),
                            service_info.get('country')
                        )

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
                            'collaborator_ids': contact_copy,
                            'follower_ids': contact_copy,
                            "end_date": end_date,
                            "start_date": start_date,
                            "city": city,
                            "country": country,
                            "service": service,
                            "end_customer": end_customer,
                            "body": ventana_body
                        }

                        tickets.append(Mount_tickets(data))

        return tickets, errors
    return None, errors


def prepare_tickets(services_info, start_date, end_date, down_time, location, description, customer_contact_info):
    customer_contact, customer_name = customer_contact_info
    services = []
    # the service who will be create main ticket
    customer_service = list(services_info.keys())[0]

    # requester_id = 1266469881070  # REQUEST FOR TEST
    # contact_copy = [21200390635547]      # EMAIL IN COPY
    # get the other ids to send as a copy the ticket
    requester_id = customer_contact.split(",")[0]  # prod
    contact_copy = customer_contact  # prod
    for service in services_info:
        status = services_info[service]['status'].lower()
        if 'delivered' in status:
            services.append(service)

    city = services_info[customer_service].get('cidade')
    country = services_info[customer_service].get('pais')
    end_customer = services_info[customer_service].get('clienteFinal')
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
        'collaborator_ids': contact_copy,
        'follower_ids': contact_copy,
        "end_date": end_date,
        "start_date": start_date,
        "city": city,
        "country": country,
        "service": service,
        "end_customer": end_customer,
        "body": ventana_body
    }

    ticket_data = Mount_tickets(data)

    return ticket_data, services


def update_tickets(ticket, core_id, core_data_activity):
    """
    Update Zendesk tickets with information about maintenance window and core activity.

    :param tickets: Comma-separated string of ticket IDs.
    :param core_id: ID of the core associated with the activity.
    """
    core_date = datetime.fromisoformat(core_data_activity)
    if ticket and core_id:
        payload = {
            "ticket": {
                "comment": {
                    "html_body": f"<p align='center'><b>MAINTENANCE WINDOW - Core Activity {core_id} - {core_date.strftime('%Y-%m-%d %H:%M')} GMT-3 .</b></p>",
                    "public": False
                }
            }
        }

        url_update = f"{ZENDESK_URL}/api/v2/tickets/{ticket}"

        response = requests.put(url_update, headers=headers, json=payload)
        print(response.json())


def create_ticket(data_ticket):
    if data_ticket:
        payload = {"ticket": data_ticket}

        # Used requests.post instead of requests.request
        response = requests.post(url=url, headers=headers, json=payload)
        ticket_id = response.json()['ticket']['id']

        return ticket_id
    else:
        return None


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


def generate_tickets_zendesk(data):
    ''' this function will receive data type dict from frontend 

    data = {'form_core''core_form', 'services':dict(all service for the same customer and their info neeeded, 'contacts': 'customer info from qb to generate tickets) }

    return error and tickets 

    core in quickbase is generated in GMT-3, but our customer receive the tickets in UTC, so that we have to ajust the data and add +3 to reach the UTC TIME


    '''
    print(data)
    id = data.get('id')
    core_id = data.get('core_id')
    start_date = data.get('form_core').get('start_date')
    end_date = data.get('form_core').get('end_date')
    start_date_zendesk_format = Ajust_date(start_date)
    end_date_zendesk_format = Ajust_date(end_date)
    services = data.get('services').get('attributes')
    down_time = data.get('form_core').get('downtime')
    location = data.get('form_core').get('location')

    # this description for ticket is different with core descriptions, because the customer will receive
    description = data.get('form_core').get('Description_to_customers')
    customer_contact_info = data.get('services').get('contacts')

    # print("Services:", services)
    # print("Start Date:", start_date_zendesk_format)
    # print("End Date:", end_date_zendesk_format)
    # print("Down Time:", down_time)
    # print("Location:", location)
    # print("Description:", description)
    # print("customer_contact_info:", customer_contact_info)

    data_tickets, services = prepare_tickets(services_info=services, start_date=start_date_zendesk_format,
                                             end_date=end_date_zendesk_format, down_time=down_time, location=location, description=description, customer_contact_info=customer_contact_info)

    if data_tickets:
        ticket_number = create_ticket(data_tickets)
        print("Ticket Number:", ticket_number)
        print("Ticket Number:", type(ticket_number))

        # ticket_number = '1010'
        update_tickets_and_affected_services_for_core(
            id=id, new_ticket_info=str(ticket_number), new_affected_services=services)
        update_tickets(ticket_number, core_id, core_data_activity=start_date)
        return ticket_number
    else:
        ticket_numbers = 'None Ticket generated'
        return ticket_numbers
