import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
from jinja2 import Template
import logging


logging.basicConfig(level=logging.INFO, filename='log_emails.txt',
                    format="%(asctime)s %(message)s")


class EmailNotification:
    def __init__(self):
        # Load environment variables from the .env file
        load_dotenv()
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.to_email = 'lucasfacsul@hotmail.com'
        self.logo_url = 'https://static.wixstatic.com/media/7e4e6f_29d3996755c4460ab5fed99424c9db85~mv2.png/v1/crop/x_57,y_221,w_1446,h_369/fill/w_255,h_65,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/Logotipo%20IG_Mesa%20de%20trabajo%201.png'

    def generate_notification_template(self, core_id, tickets):
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
                    <img src="{{ logo }}" alt="Logo">
                    <h2>Maintenance Activities Notification</h2>
                    <p style="margin-bottom: 20px;" > Dear Team NOC </p>
                    <p style="margin-bottom: 50px;">A new Core Activity was created, Follow Below the Core Details  </p>
                    <h3> CORE {{ core_id }}  </h3>
                    
                    <h3> Generated Tickets  </h3>      
                    <div>    {{ tickets }}  <div>  
                </div>
            </div>
        </body>
        </html>
        """

        context = {'core_id': core_id,
                   'tickets': tickets, 'logo': self.logo_url}
        template = Template(template_string)
        output = template.render(context)
        return output

    def send_notification(self, core_id, tickets, date):
        logging.info(
            "data received from send_notification function %s %s", core_id, tickets)

        subject = f'PLANNED ACTIVITY CORE {core_id} {date}'
        content = self.generate_notification_template(core_id, tickets)

        msg = EmailMessage()
        msg.add_alternative(content, subtype='html')

        msg['Subject'] = subject
        msg['From'] = self.smtp_username
        msg['To'] = self.to_email

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Use TLS
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")
            logging.error(f"Error sending email: {e}")
