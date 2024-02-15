from get_contacts_from_quickbase import get_customers_contact
from quickbase_requests import Get_service_info
from generate_tickets_zendesk import Mount_tickets, generate_notification_template
import json
import re


def create_tickets(services, start_date, end_date, down_time, location):
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
            "html_body": ventana_body
        }

        tickets.append(Mount_tickets(data))
    return tickets


# start_date = '01/01/2023 02:00'
# end_date = '01/01/2023 03:00'
# down_time = '04:00'
# location = ' SAO PAULO BRASIL '
# circuito = ''' VZB.5511.A005
# VZB.5511.A001
# VZB.5511.A002 
# GTT.5511.A002 '''
# resultado = create_tickets(services=circuito, start_date=start_date,
#                            end_date=end_date, down_time=down_time, location=location)
# print(len(resultado))
# print(resultado[1]['comment'])
