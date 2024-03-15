import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
from jinja2 import Template
from googleapiclient.discovery import build
import httplib2
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
import base64
from googleapiclient.errors import HttpError
from email.message import EmailMessage

# Load environment variables from the .env file
load_dotenv()


def Auth_Gmail():

    current_directory = os.getcwd()

    credentials_file_path = os.path.join(current_directory, 'credentials_gmail.json')

    CLIENT_ID = os.getenv('CLIENT_ID_MAIL_MW')

    CLIENT_SECRET = os.getenv('SECRET_MAIL_MW')

    OAUTH_SCOPE = 'https://mail.google.com/'

    REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

    storage = Storage(credentials_file_path)
    
    credentials = storage.get()
    if not credentials:
        # Run through the OAuth flow and retrieve credentials
        flow = OAuth2WebServerFlow(
            CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
        authorize_url = flow.step1_get_authorize_url()
        print('Go to the following link in your browser: ' + authorize_url)
        code = input('Enter verification code: ').strip()
        credentials = flow.step2_exchange(code)
        storage.put(credentials)
    http = httplib2.Http()
    http = credentials.authorize(http)
    return http


class EmailNotification:
    def __init__(self):
        self.to_email = os.getenv('EMAIL_TO')
        self.from_email = os.getenv('EMAIL_FROM')
        self.logo_url = 'https://static.wixstatic.com/media/7e4e6f_29d3996755c4460ab5fed99424c9db85~mv2.png/v1/crop/x_57,y_221,w_1446,h_369/fill/w_255,h_65,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/Logotipo%20IG_Mesa%20de%20trabajo%201.png'
        self.cred = Auth_Gmail()

    def generate_notification_template(self, core_id, tickets):
        '''

        Create a template 

        '''
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
                        color: black;
                        width: 80%;
                        max-width: 1000px;
                        background-color: #2196F3;
                        margin: 0 auto;
                        padding: 10px;
                        border-radius: 10px;
                        box-shadow: 17px 20px 20px 20px rgba(0,0,0,0.2);
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
                    {% if tickets %}
                    <ul>
                        {% for ticket in tickets %}
                            <li>{{ ticket }}</li>
                        {% endfor %}
                    </ul>
                    {% else %}
                        <p>No generated tickets</p>
                    {% endif %}
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
        ''' This function receive data when it`s callled and create a template 
        email and send to noc informing the core maintenance and the tickets generated

        '''
        service = build('gmail', 'v1', http=self.cred)

        date_formated = date.split("T")[0]
        hours = date.split("T")[1]
        subject = f'PLANNED ACTIVITY CORE {core_id} {date_formated} {hours} GMT-3'
        content = self.generate_notification_template(core_id, tickets)

        msg = EmailMessage()

        msg.add_alternative(content, subtype='html')

        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = self.to_email

        try:
            # encoded message
            encoded_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            create_message = {"raw": encoded_message}
            # pylint: disable=E1101
            send_message = (
                service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
            print(f'Message Id: {send_message["id"]}')
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")
