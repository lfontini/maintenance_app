from pyzabbix import ZabbixAPI, ZabbixAPIException
from datetime import datetime
import pytz
from dotenv import load_dotenv
import os
# load enviroments variables
load_dotenv()
ZABBIX_URL = os.environ.get("ZABBIX_URL")
USER_ZABBIX = os.environ.get("USER_ZABBIX")
PASS_ZABBIX = os.environ.get("PASS_ZABBIX")


def get_host_ids(services):
    """Get Zabbix host IDs for the provided services.

    Args:
        services (list): List of service names.

    Returns:
        list: List of Zabbix host IDs.
    """
    host_ids = []

    # Connect to Zabbix API
    zapi = ZabbixAPI(ZABBIX_URL)
    zapi.login(USER_ZABBIX, PASS_ZABBIX)

    try:
        for service in services:
            hosts = zapi.host.get(search={"host": service})
            if hosts:
                host_id = hosts[0]["hostid"]
                host_ids.append(host_id)
                print(host_id)

    except ZabbixAPIException as e:
        print(f"Zabbix API Error: {e}")

    finally:
        # Disconnect from Zabbix API
        if 'zapi' in locals():
            zapi.user.logout()

    return host_ids


def adjust_date(date):
    """Adjust the date format and convert it to UTC.

    Args:
        date (str): Input date string.

    Returns:
        datetime: Adjusted date in UTC.
    """
    current_date_format = date
    entry_format_date = "%Y-%m-%dT%H:%M"

    try:
        # Convert the input date string to a datetime object in GMT-3
        local_tz = pytz.timezone('America/Sao_Paulo')  # Assuming GMT-3
        converted_date = local_tz.localize(
            datetime.strptime(current_date_format, entry_format_date))

        # Convert to UTC
        converted_date_utc = converted_date.astimezone(pytz.utc)

        return converted_date_utc
    except ValueError as e:
        print(f"Error parsing date: {e}")
        return None


def create_maintenance_window(name, start_time, end_time, host_ids=None):
    """Create a Zabbix maintenance window.

    Args:
        name (str): Name of the maintenance window.
        start_time (int): Start time of the maintenance window (timestamp).
        end_time (int): End time of the maintenance window (timestamp).
        host_ids (list): List of Zabbix host IDs.

    Returns:
        dict: Result of the Zabbix API call.
    """
    try:
        # Connect to Zabbix API
        zapi = ZabbixAPI(ZABBIX_URL)
        zapi.login(USER_ZABBIX, PASS_ZABBIX)

        # Configure maintenance window parameters
        maintenance_params = {
            "name": name,
            "active_since": start_time,
            "active_till": end_time,
            "tags_evaltype": 0,
            "hostids": host_ids,
            "timeperiods": [
                {
                    "period": end_time - start_time,
                    "timeperiod_type": 0,
                }
            ]
        }
        print('maintenance_params', maintenance_params)
        # Call the Zabbix API to create the maintenance window
        result = zapi.maintenance.create(maintenance_params)

        return result

    except ZabbixAPIException as e:
        print(f"Zabbix API Error: {e}")

    finally:
        # Disconnect from Zabbix API
        if 'zapi' in locals():
            zapi.user.logout()


def create_zabbix_maintenance(services, start_maintenance, end_maintenance, core_id):
    """Create a Zabbix maintenance window for specified services.

    Args:
        services (list): List of service names.
        start_maintenance (str): Start time of the maintenance window.
        end_maintenance (str): End time of the maintenance window.
        core_id (str): Core ID for the maintenance window.


    # Example usage
    create_zabbix_maintenance(
        ["ITR.5511.A002", "A1T.562.D001", "A1T.562.D002"],
        "2023-01-03T18:21:00",
        "2023-01-03T19:21:00",
        '2768'


    """
    # Get host IDs from Zabbix by searching for service names
    host_ids = get_host_ids(services)
    print("hostid ", host_ids)
    print("numero de ids ", len(host_ids))

    adjusted_date_start = adjust_date(start_maintenance)
    adjusted_date_end = adjust_date(end_maintenance)

    if adjusted_date_start and adjusted_date_end:
        window_name = f"Maintenance CORE {core_id}"
        start_time = int(adjusted_date_start.timestamp())
        end_time = int(adjusted_date_end.timestamp())

        result = create_maintenance_window(
            window_name,
            start_time,
            end_time,
            host_ids=host_ids
        )

        if result is not None:
            print(
                f"Maintenance window created with ID: {result['maintenanceids'][0]}")
            return result['maintenanceids'][0]
        else:
            return f'Not generated ERROR {result}'
