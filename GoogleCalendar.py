import pickle
import os
from Logger import write_log
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime
from HLTVCrawler import CrawledEvent


class Calendar:
    def __init__(self):
        self.__scopes = ["https://www.googleapis.com/auth/calendar"]
        self.__timezone = "Europe/Berlin"

    def __is_already_authenticated(self):
        if os.path.isfile(".gitignore/token.pkl"):
            return True
        return False

    def __load_credentials(self):
        with open(".gitignore/token.pkl", "rb") as file:
            return pickle.load(file)

    def __save_credentials(self, credentials):
        with open(".gitignore/token.pkl", "wb") as file:
            pickle.dump(credentials, file)

    def __google_authentication(self):
        if self.__is_already_authenticated() is True:
            return self.__load_credentials()
        else:
            flow = InstalledAppFlow.from_client_secrets_file(".gitignore/client_secret.json", scopes=self.__scopes)
            flow.run_console(access_type='offline')
            self.__save_credentials(flow.credentials)
            return flow.credentials

    def __create_sevice(self):
        credentials = self.__google_authentication()
        service = build("calendar", "v3", credentials=credentials)
        return service

    def __save_calendar_id(self, id):
        with open("calendarID.txt", "w") as file:
            file.write(id)

    def __load_calendar_id(self):
        with open("calendarID.txt", "r") as file:
            return file.readline().strip()

    def __does_calendar_id_file_exist(self):
        if os.path.isfile("calendarID.txt") is True:
            return True
        return False

    def __create_new_calendar(self):
        service = self.__create_sevice()
        calendar = {
            'summary': 'HLTV CSGO Events',
            'timeZone': self.__timezone
        }
        created_calendar = service.calendars().insert(body=calendar).execute()
        calendar_id = created_calendar["id"]
        self.__save_calendar_id(calendar_id)
        return calendar_id

    def __get_calendar_id(self):
        if self.__does_calendar_id_file_exist() is True:
            return self.__load_calendar_id()
        return self.__create_new_calendar()

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
        return event["id"]

    def delete_event(self, event_id):
        service = self.__create_sevice()
        calendar_id = self.__get_calendar_id()
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

    def update_event(self, event_id, new_title, new_start_time, new_end_time, new_description):
        self.delete_event(event_id)
        self.create_event(new_title, new_start_time, new_end_time, new_description)

    def fetch_events(self):
        calendar_events = []
        page_token = None
        service = self.__create_sevice()
        while True:
            events = service.events().list(calendarId=self.__get_calendar_id(), pageToken=page_token).execute()
            for event in events['items']:
                title = event["summary"]
                start_time = self.turn_into_date_obj(event['start']["dateTime"])
                end_time = self.turn_into_date_obj(event['end']["dateTime"])
                description = event['description']
                event_id = event["id"]
                calendar_events.append(CrawledEvent(title, start_time, end_time, description, event_id))
            page_token = events.get('nextPageToken')
            if not page_token:
                break
        return calendar_events

    def turn_into_date_obj(self, date_str):
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")


calendar = Calendar()
