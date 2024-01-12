import requests
from jinja2 import Template
import time
import json


def generate_notification_template():
    # html template
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

            <p style="margin-bottom: 20px;" > Dear Team </p>

            
            
            <p style="margin-bottom: 20px;"class="title">We would like to inform you that the maintenance windows has been cancelled </p>
            <p style="margin-bottom: 50px;">we will plan another date and keep you posted.</p>
            <p>Thank you,</p>

        </div>
    </div>
</body>

</html>

    """

    return template_string


headers = {
    'Authorization': 'Basic bm9jQGlnbmV0d29ya3MuY29tL3Rva2VuOk8yUTdYeGZScUxJOHF2MEF1NGxtSk10NnVEOHhqTU1wdUlrUU96YUI=',
    'Content-Type': 'application/json'
}


def make_request_zendesk(method, url, body):

    response = requests.put(url, headers=headers,
                            json=body)  # Alterado para PUT
    return response


def cancel_tickets(tickets):
    print('tickets', tickets)
    if len(tickets) < 1:
        print("Nenhum ticket encontrado")
        return None
    elif len(tickets) == 1:
        print("one tickets")

        # Corrigido para acessar o primeiro ticket da lista
        url = f"https://ignetworks.zendesk.com/api/v2/tickets/{tickets[0]}"
        template = generate_notification_template()
        body = {
            "ticket": {
                "comment": {
                    "html_body": template,
                    "public": True
                },
                "status": "solved"
            }
        }
        response = make_request_zendesk('PUT', url, body)
        return tickets[0]
    else:
        print("many tickets")
        tickets_str = ','.join(tickets)
        # Removida a barra dupla
        url = f"https://ignetworks.zendesk.com/api/v2/tickets/update_many.json?ids={tickets_str}"
        template = generate_notification_template()
        body = {
            "ticket": {
                "comment": {
                    "html_body": template,
                    "public": True
                },
                "status": "solved"
            }
        }
        response = make_request_zendesk('PUT', url, body)
        print(response)
        status_request = response.json()['job_status']['status']
        request_url = response.json()['job_status']['url']
        if True:
            if response.ok:
                while (status_request != "completed"):
                    response1 = requests.get(request_url,  headers=headers)
                    print(response1)
                    status_request = response1.json()['job_status']['status']
                    time.sleep(2)
                if status_request == "completed":
                    ticket_ids = ','.join(
                        [str(item['id']) for item in response1.json()['job_status']['results']])

                return ticket_ids
