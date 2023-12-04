import subprocess
import re
from .getdevice import Get_Device_Data, Get_Device_Data_From_Quickbase
from netmiko import ConnectHandler
from netmiko.ssh_dispatcher import ConnectHandler
import os
from dotenv import load_dotenv
import requests
import concurrent.futures

# Load the .env file .env
load_dotenv()
HOSTNAME_QB = os.environ.get("HOSTNAME_QB")
TOKEN_QB = os.environ.get("TOKEN_QB")
headers = {
    'QB-Realm-Hostname': HOSTNAME_QB,
    'User-Agent': '{User-Agent}',
    'Authorization': TOKEN_QB
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


def status_qb(circuito):
    '''
       this function will return quickbase status


     '''
    status = fetch_activity_data(
        "bfwgbisz4", [36], where="{7.CT." + f"'{circuito}'"+"}")[0]
    return status


def Access_Device(ip, manufacturer):
    '''
        This function will connect to the device and return the netmiko object
        :param ip: The ip of the device
        :param fabricante: The manufacturer of the device
        :return: netmiko object
        :rtype: object

     '''

    USERNAME_MIKROTIK_CPE = os.environ.get("USERNAME_MIKROTIK_CPE")
    PASSWORD_MIKROTIK_CPE = os.environ.get("PASSWORD_MIKROTIK_CPE")
    TACACS_USER = os.environ.get("TACACS_USER")
    TACACS_PASSWORD = os.environ.get("TACACS_PASSWORD")

    try:
        if manufacturer.lower() == 'mikrotik':

            net_connect = ConnectHandler(
                device_type='mikrotik_routeros',
                host=ip,
                username=USERNAME_MIKROTIK_CPE,
                password=PASSWORD_MIKROTIK_CPE,
                port=22
            )

        elif manufacturer.lower() == 'cisco systems':
            net_connect = ConnectHandler(
                device_type='autodetect',
                host=ip,
                username=TACACS_USER,
                password=TACACS_PASSWORD
            )
        else:
            net_connect = ConnectHandler(
                device_type='autodetect',
                host=ip,
                username=TACACS_USER,
                password=TACACS_PASSWORD
            )

        return net_connect
    except:
        return None


def PingTest(ip):
    '''
        This function will test the ping of the device
        :param ip: The ip of the device
        :return: The ping of the device
        :rtype: string


     '''
    treated_ip = ip.split("/")[0]
    print(treated_ip, 'treated_ip')
    ping = subprocess.getoutput(f"ping  {treated_ip} ")
    print(ping)
    return ping


# ... (your other imports)


def TestService(circuito):
    result = {}
    RESULTADO_FINAL = []
    ip_address = Get_Device_Data(circuito)

    if 'none' in ip_address['ip']:
        print("esta procurando no quickbase")
        ip_address = Get_Device_Data_From_Quickbase(circuito)
        print('ip_address', ip_address)
    if not 'none' in ip_address['ip'] and ip_address['manufacturer']:
        print("entrou aqui ")
        ip = ip_address['ip']
        fabricante = ip_address['manufacturer']
        result['circuito'] = circuito
        if ip != 'none':
            ping = PingTest(ip)
            treated_ip = ip.split("/")[0]
            if 'Enviados = 4, Recebidos = 4,' in ping:
                result['resultadoping'] = f'Ping to {treated_ip} UP'

            else:
                result['resultadoping'] = f'Ping to {treated_ip} DOWN'
        else:
            result['resultadoping'] = f'Ip not found'
        net_connect = Access_Device(
            ip.split("/")[0], fabricante)  # Corrected index here
        print("Try connecting... ", fabricante, ip.split("/")[0])
        if net_connect:
            try:
                if fabricante.lower() == 'mikrotik':
                    traffic_measure = net_connect.send_command(
                        "interface monitor-traffic ether5 once", use_textfsm=True)
                    treated_bandwidth = traffic_measure.split()

                    print(type(treated_bandwidth))

                    Index_rx = treated_bandwidth.index("rx-bits-per-second:")
                    Index_tx = treated_bandwidth.index("tx-bits-per-second:")

                    rx = treated_bandwidth[Index_rx + 1]
                    tx = treated_bandwidth[Index_tx + 1]

                    rx_int = rx[0]

                    if rx_int == "0":
                        print("No Traffic")
                        print(f"traffic  RX: {rx}  TX: {tx} ")

                        result['status'] = "Mikrotik DOWN"
                        result['interfacestatus'] = f'Upload: {tx}, Download: {rx}'

                    else:
                        print(f"traffic  RX: {rx} e TX: {tx} ")
                        result['status'] = "Mikrotik UP"
                        result['interfacestatus'] = f'Upload: {tx}, Download: {rx}'

                if 'accedian' in fabricante.lower():
                    output = net_connect.send_command(
                        "port show statistics Client").splitlines()
                    rx = output[3].split()
                    tx = output[19].split()
                    print(type(rx[3]))

                    if rx[3] and tx[3] == "0":
                        print("trafego zerado DOWN")
                        print(f"o trafego de rx é {rx[3]}")
                        print(f"o trafego de rx é {tx[3]}")
                        result['status'] = "Accedian DOWN"
                        result['interfacestatus'] = f'Upload: 0, Download: 0'

                    else:
                        print("trafego  UP")
                        print(f"o trafego de rx é {rx[3]}")
                        print(f"o trafego de rx é {tx[3]}")
                        result['status'] = "Accedian UP"
                        result['interfacestatus'] = f'Upload: {tx[3]}, Download: {rx[3]}'

                elif fabricante.lower() == 'cisco':
                    output_raw = net_connect.send_command(
                        "show interfaces FastEthernet0")
                    input_match = re.search(r"(\d+) bits/sec", output_raw)
                    output_match = re.search(r"(\d+) bits/sec", output_raw)

                    if input_match and output_match:
                        print("entrou aqui 2 ")
                        input_rate = input_match.group(1)
                        output_rate = output_match.group(1)
                        result['interfacestatus'] = f'Upload: {output_rate} bits/sec , Download :{input_rate} bits/sec'
                        result['status'] = "Cisco Systems UP"
                    else:
                        print("entrou aqui 2 ")

                        result['status'] = "Cisco Systems DOWN"
                        result['interfacestatus'] = "No Traffic"
                else:
                    result['circuito'] = f"{circuito}"
                    result['status'] = "Equipment unreacheable or not in Netbox DOWN"
                    result['interfacestatus'] = "None data retrived"

            except:
                result['circuito'] = f"{circuito}"
                result['status'] = "Equipment unreacheable or not in Netbox DOWN"
                result['interfacestatus'] = "None data retrived"
        else:
            result['circuito'] = circuito
            result['status'] = 'Equipment unreacheable or not in Netbox/QB DOWN'
            result['interfacestatus'] = "None data retrived"

        result['statusquickbase'] = status_qb(circuito)
        RESULTADO_FINAL.append(result)

        return RESULTADO_FINAL
    else:
        print("entoru aqui")
        result['circuito'] = f"{circuito}"
        result['status'] = 'NONE DATA FOUND, '
        result['resultadoping'] = 'NO IP ADDRESS FOUND DOWN'
        result['interfacestatus'] = "DOWN"
        result['statusquickbase'] = status_qb(circuito)
        RESULTADO_FINAL.append(result)
        return RESULTADO_FINAL


def Service_Validation(dados_raw):
    full_result_list = []
    services = []
    filtra_circuitos = re.findall(
        r'[a-zA-Z0-9]{3}\.[0-9]{3,5}\.[a-zA-Z][0-9]{3}', dados_raw)

    for i in filtra_circuitos:
        if i not in services:
            services.append(i)

    # You can also use ProcessPoolExecutor for processes
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(TestService, service)
                   for service in services]

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                full_result_list.extend(result)

            except Exception as e:
                print(f"An error occurred: {e}")

    return full_result_list
