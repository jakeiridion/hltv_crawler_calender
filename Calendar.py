import pickle
import os
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow


class Calendar:
    def __init__(self):
        self.__scopes = ["https://www.googleapis.com/auth/calendar"]
        self.__timezone = "UTC"
        self.__calendar_id = None

    def __is_already_authenticated(self):
        if os.path.isfile("token.pkl"):
            return True
        return False

    def __load_credentials(self):
        with open("token.pkl", "rb") as file:
            return pickle.load(file)

    def __save_credentials(self, credentials):
        with open("token.pkl", "wb") as file:
            pickle.dump(credentials, file)

    def __google_authentication(self):
        if self.__is_already_authenticated() is True:
            return self.__load_credentials()
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes=self.__scopes)
            flow.run_console()
            self.__save_credentials(flow.credentials)
            return flow.credentials

    def __create_sevice(self):
        credentials = self.__google_authentication()
        service = build("calendar", "v3", credentials=credentials)
        return service

    def __create_calendar(self):
        service = self.__create_sevice()
        calendar = {
            'summary': 'HLTV CSGO Events',
            'timeZone': self.__timezone
        }
        created_calendar = service.calendars().insert(body=calendar).execute()
        calendar_id = created_calendar["id"]
        self.__calendar_id = calendar_id
        return calendar_id

    def __does_calendar_exist(self):
        if self.__calendar_id is None:
            return False
        else:
            return True

    def __get_calendar_id(self):
        if self.__does_calendar_exist() is True:
            return self.__calendar_id
        else:
            return self.__create_calendar()

    def create_event(self, title, start_time, end_time, description):
        service = self.__create_sevice()
        calender_id = self.__get_calendar_id()

        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': self.__timezone,
            },
            'end': {
                'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': self.__timezone,
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 1440},
                ],
            },
        }

        event = service.events().insert(calendarId=calender_id, body=event).execute()
        print("Done")
        # log here


calendar = Calendar()
calendar.create_event("test", datetime(2020, 4, 1, 0, 0, 0), datetime(2020, 4, 1, 0, 0, 0) + timedelta(days=1), "description")
