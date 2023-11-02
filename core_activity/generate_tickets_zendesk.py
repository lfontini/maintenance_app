import json
from jinja2 import Template


def generate_notification_template(context):
    # Defina o template HTML
    template_string = """
<!DOCTYPE html>
<html>

<head>
    <title>Maintenance Activities Notification</title>
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
            <img src="ign.png" alt="Logo">
            <h2>Maintenance Activities Notification</h2>
            <p class="title">This ticket is to notify you of maintenance activities we will be performing on our network
                which will affect your service with sporadic flaps or outage for the following period of time.</p>
        </div>
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
                <td>Maintenance Window to improve network</td>
            </tr>
            <tr>
                <td>Location</td>
                <td>{{ city }}, {{ country }}</td>
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

    # Crie um objeto Template
    template = Template(template_string)

    # Renderize o template com o contexto
    output = template.render(context)

    return output




def Mount_tickets(data):
    ticket = {}  # Define ticket as a dictionary
    if data:
        ticket["comment"] = data['html_body']
        ticket["priority"] = "normal"
        ticket["subject"] = "Maintenance example"
        ticket["assignee_id"] = 16632994687
        ticket["status"] = "open"
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
