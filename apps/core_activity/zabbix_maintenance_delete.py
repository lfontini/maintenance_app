import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

ZABBIX_URL = os.environ.get("ZABBIX_URL")
USER_ZABBIX = os.environ.get("USER_ZABBIX")
PASS_ZABBIX = os.environ.get("PASS_ZABBIX")


def zabbix_login(url, user, password):
    """
    Perform login to the Zabbix server and return the authentication token.

    Parameters:
        url (str): Zabbix server URL.
        user (str): User name for login.
        password (str): Password associated with the user name.

    Returns:
        str: Authentication token if login is successful, None otherwise.
    """
    login_data = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": user,
            "password": password,
        },
        "id": 1,
    }
    response = requests.post(url, data=json.dumps(login_data), headers={
                             "Content-Type": "application/json"})
    result = response.json().get("result")
    return result


def make_request_zabbix(url, auth_token, maintenance_ids):
    """
    Delete maintenances on the Zabbix server.

    Parameters:
        url (str): Zabbix server URL.
        auth_token (str): Authentication token obtained during login.
        maintenance_ids (list): List of maintenance IDs to be deleted.

    Returns:
        dict: Dictionary containing the response of the maintenance deletion.
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "maintenance.delete",
        "params": maintenance_ids,
        "id": 1,
        "auth": auth_token,
    }
    response = requests.post(url, data=json.dumps(payload), headers={
                             "Content-Type": "application/json"})
    return response.json()


def delete_maintenance_zabbix(maintenance_id):
    """
    Delete a specific maintenance on the Zabbix server.

    Parameters:
        maintenance_id (str): ID of the maintenance to be deleted.

    Returns:
        str: 'ok' if deletion is successful, None otherwise.
    """
    auth_token = zabbix_login(ZABBIX_URL, USER_ZABBIX, PASS_ZABBIX)

    if auth_token:
        maintenance_ids_to_delete = [maintenance_id]
        delete_result = make_request_zabbix(
            ZABBIX_URL, auth_token, maintenance_ids_to_delete)

        if delete_result.get("result") is not None:
            return 'ok'
        else:
            print(f"Error deleting maintenances: {delete_result.get('error')}")
            return None
    else:
        print("An error occurred while accessing the Zabbix API.")
        return None
