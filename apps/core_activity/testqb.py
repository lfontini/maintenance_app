import os
from dotenv import load_dotenv
import re
import concurrent.futures
from quickbase_requests import Get_service_info
from quickbase_requests import get_customers_contact

# load environment variables
load_dotenv()
HOSTNAME_QB = os.environ.get("HOSTNAME_QB")
TOKEN_QB = os.environ.get("TOKEN_QB")


def identify_services(raw_data):
    service_info = {}
    services = set(re.findall(
        r'[a-zA-Z0-9]{3}\.[0-9]{3,5}\.[a-zA-Z][0-9]{3}', raw_data))
    print(len(services))

    if services:
        prefixes_and_contacts = {}

        def process_prefix(prefix):
            prefixes_and_contacts[prefix] = get_customers_contact(prefix)

        prefixes = []
        for service in services:
            prefixe = service.split(".")[0]
            if prefixe not in prefixes:
                prefixes.append(prefixe)
        # Use concurrent.futures para processar os prefixos em paralelo
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(process_prefix, prefixes)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit tasks for each service to the executor
            future_to_service = {executor.submit(
                Get_service_info, service): service for service in services}

            # Wait for the tasks to complete and collect the results
            for future in concurrent.futures.as_completed(future_to_service):
                service = future_to_service[future]
                try:
                    service_info[service] = future.result()
                except Exception as e:
                    print(f"Error fetching info for {service}: {e}")

        return service_info, prefixes_and_contacts
    else:
        return None, None


services_data = '''

         TTA.571.A001    GTT.5932.A001    GTT.52735.A001    AXT.1214.N001    CLR.1773.A001    CLR.1855.A001    CLR.1214.N001    CLR.1281.A001    CLR.1303.A001    AXT.1305.A001    AXT.3491.A001    TSY.52442.A004    TSY.52656.A001    TSY.562.A024    GTT.1214.N001    GTT.5255.A011    TTA.571.A001    TLS.52449.A003    GTT.5255.A009    GCX.1480.A002    GCX.52722.A001    GCX.52442.A002    VTL.1214.N001    TSY.52222.A002    TSY.52474.A001    TSY.5281.A005    TSY.52417.A001    TSY.52222.A003    TSY.52477.A001    TSY.52722.A001    TSY.52442.A002    TSY.5281.A007    TSY.5255.A002    TSY.562.A012    TSY.5042.A005    TSY.52473.A001    ITR.52442.A001    GTT.5255.A011     
'''
service_info, prefixes_and_contacts = identify_services(
    services_data)



print(service_info)
print(prefixes_and_contacts)
customer_info = prefixes_and_contacts.get('VTL', None)
if customer_info is not None:
    print("aaaaa", customer_info[0].split(",")[0])
