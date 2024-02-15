import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Define the root directory of your project


# obs token and credencials should be in the same folder and the root path / in paralel with
# maintenance_django folder

class EventCreator:
    '''
    This class creates events in Google Calendar.
    '''

    def __init__(self, calendar_title, start_time, end_time, description):
        self.calendar_title = calendar_title
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
        self.credentials = self.get_credentials()

    def get_credentials(self):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return creds

    def create_event(self):
        try:
            service = build("calendar", "v3", credentials=self.credentials)

            event = {
                'summary': self.calendar_title,
                'description': self.description,
                'start': {
                    'dateTime': self.start_time,
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': self.end_time,
                    'timeZone': 'America/Sao_Paulo',
                },
            }
            print(event)
            event = service.events().insert(calendarId='primary', body=event).execute()
            print(event)
            print('Event created: %s' % (event.get('htmlLink')))

        except HttpError as error:
            print(f"An error occurred: {error}")

