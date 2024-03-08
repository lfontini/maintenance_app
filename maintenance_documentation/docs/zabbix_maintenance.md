# ZABBIX MAINTENANCE 

## What is it? 
Overview
You can define maintenance periods for host groups, hosts and specific triggers/services in Zabbix.

There are two maintenance types - with data collection and with no data collection.

During a maintenance "with data collection" triggers are processed as usual and events are created when required. However, problem escalations are paused for hosts/triggers in maintenance, if the Pause operations for suppressed problems option is checked in action configuration. In this case, escalation steps that may include sending notifications or remote commands will be ignored for as long as the maintenance period lasts. Note that problem recovery and update operations are not suppressed during maintenance, only escalations.

For example, if escalation steps are scheduled at 0, 30 and 60 minutes after a problem start, and there is a half-hour long maintenance lasting from 10 minutes to 40 minutes after a real problem arises, steps two and three will be executed a half-hour later, or at 60 minutes and 90 minutes (providing the problem still exists). Similarly, if a problem arises during the maintenance, the escalation will start after the maintenance.

To receive problem notifications during the maintenance normally (without delay), you have to uncheck the Pause operations for suppressed problems option in action configuration.

Source [Link to Zabbix Maintenance Documentation](https://www.zabbix.com/documentation/current/en/manual/maintenance)


![zabbix](/media/maintenance_zabbix.png)







This code provides functions to interact with the Zabbix API for creating maintenance windows. Here's an overview of the key functions:

1. `update_zabbix_id_into_core(id, zabbix_id)`: Updates the Zabbix ID into the existing Core database.

2. `get_host_ids(services)`: Retrieves Zabbix host IDs for the provided services.

3. `adjust_date(date)`: Adjusts the date format and adds 3 hours to convert it to UTC. 

4. `create_maintenance_window(name, start_time, end_time, host_ids=None)`: Creates a Zabbix maintenance window.

5. `create_zabbix_maintenance(id, services, start_maintenance, end_maintenance, core_id)`: Creates a Zabbix maintenance window for specified services.

## Functions

### `update_zabbix_id_into_core(id, zabbix_id)`

This function updates the Zabbix ID into the existing Core database.

- `id` (int): ID of the Core.
- `zabbix_id` (str): Zabbix ID to be included.

### `get_host_ids(services)`

This function retrieves Zabbix host IDs for the provided services.

- `services` (list): List of service names.
- Returns: List of Zabbix host IDs.

### `adjust_date(date)`

This function adjusts the date format and adds 3 hours to convert it to UTC.

- `date` (str): Input date string.
- Returns: Adjusted date in UTC.

### `create_maintenance_window(name, start_time, end_time, host_ids=None)`

This function creates a Zabbix maintenance window.

- `name` (str): Name of the maintenance window.
- `start_time` (int): Start time of the maintenance window (timestamp).
- `end_time` (int): End time of the maintenance window (timestamp).
- `host_ids` (list): List of Zabbix host IDs.
- Returns: Result of the Zabbix API call.

### `create_zabbix_maintenance(id, services, start_maintenance, end_maintenance, core_id)`

This function creates a Zabbix maintenance window for specified services.

- `services` (list): List of service names.
- `start_maintenance` (str): Start time of the maintenance window.
- `end_maintenance` (str): End time of the maintenance window.
- `core_id` (str): Core ID for the maintenance window.

### code 

``` 


def update_zabbix_id_into_core(id, zabbix_id):
    """
    Include zabbix id into existent core db

    """

    try:
        core = Core.objects.get(id=id)
    except Core.DoesNotExist:
        # Core with the provided ID not found
        return False

    # Append or update the ticket information
    if core.zabbix_maintenance_id:
        # If there are existing tickets, append the new ticket information
        core.zabbix_maintenance_id = zabbix_id
    else:
        # If no existing tickets, set the new ticket information
        core.tickets_zendesk_generated = 'None'

    # Save the changes
    core.save()

    # Return True if the update is successful
    return True


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
    """Adjust the date format and add 3 hours to convert it to UTC.

    Args:
        date (str): Input date string.

    Returns:
        datetime: Adjusted date in UTC.
    """
    entry_format_date = "%Y-%m-%dT%H:%M"

    try:
        # Convert the input date string to a datetime object in GMT-3
        local_tz = pytz.timezone('America/Sao_Paulo')  # Assuming GMT-3
        converted_date = datetime.strptime(date, entry_format_date)
        localized_date = local_tz.localize(converted_date, is_dst=None)

        # Add 3 hours
        adjusted_date = localized_date + timedelta(hours=3)

        print('adjusted_date', adjusted_date)
        return adjusted_date
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


def create_zabbix_maintenance(id, services, start_maintenance, end_maintenance, core_id):
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

    print("start_maintenance", start_maintenance)
    adjusted_date_start = adjust_date(start_maintenance)
    print("end_maintenance", end_maintenance)
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
            update_zabbix_id_into_core(
                id=id, zabbix_id=result['maintenanceids'][0])
            print(
                f"Maintenance window created with ID: {result['maintenanceids'][0]}")
            return result['maintenanceids'][0]
        else:
            return f'Not generated ERROR {result}'
```