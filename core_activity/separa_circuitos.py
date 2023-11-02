from get_contacts_from_quickbase import get_customers_contact
from quickbase_requests import Get_service_info
from generate_tickets_zendesk import Mount_tickets, generate_notification_template

a = ['VZB.5511.A021', 'VZB.5511.A021', 'VZB.5511.A022',
     'VZB.5511.A024', 'VZB.5511.A023', 'GTT.5519.A004']
tickets = []
start_date = '01/05/2023'
end_date = '01/05/2023'
down_time = '4:00'


def create_tickets():
    Erase_duplicates = set(a)
    customers = {}
    for circuit in Erase_duplicates:
        customer_prefix = circuit.split(".")[0]
        if customer_prefix not in customers:
            customers[customer_prefix] = []
        customers[customer_prefix].append(circuit)

    for customer in customers.keys():
        service = customers[customer][0]
        services = customers[customer]
        contact_list, customer_name = get_customers_contact(customer)
        id, address, end_customer, city, country = Get_service_info(
            customers[customer][0])

        context = {
            'start_date': start_date,
            'end_date':  end_date,
            'downtime': down_time,
            'city': city,
            'country': country,
            'services': services,
        }

        ventana_body = generate_notification_template(context)

        data = {
            "requester_id": 1266469881070,
            "end_date": end_date,
            "start_date": start_date,
            "city": city,
            "country": country,
            "service": service,
            "end_customer": end_customer,
            "html_body": ventana_body
        }

        tickets.append(Mount_tickets(data))
        print(tickets)


print(create_tickets())
