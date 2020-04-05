import pickle
import os
from dependencies.Logger import write_log
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from datetime import datetime
from dependencies.HLTVCrawler import CrawledEvent
from dependencies.ConfigReader import config


class Calendar:
    def __init__(self):
        self.__scopes = ["https://www.googleapis.com/auth/calendar"]
        self.__timezone = str(config.timezone)
        self.client_secret_path = config.client_secret_path
        self.token_path = os.path.join("dependencies", "token.pkl")
        self.calendar_id_path = os.path.join("dependencies", "calendarID.txt")

    def is_already_authenticated(self):
        if os.path.isfile(self.token_path):
            return True
        return False

    def __load_credentials(self):
        with open(self.token_path, "rb") as file:
            return pickle.load(file)

    def __save_credentials(self, credentials):
        with open(self.token_path, "wb") as file:
            pickle.dump(credentials, file)
            write_log("authorization token saved in " + self.token_path)

    def __google_authentication(self):
        if self.is_already_authenticated() is True:
            return self.__load_credentials()
        else:
            try:
                write_log("Authorizing the application.")
                flow = InstalledAppFlow.from_client_secrets_file(config.client_secret_path, scopes=self.__scopes)
                flow.run_console(access_type='offline')
                self.__save_credentials(flow.credentials)
                return flow.credentials
            except InvalidGrantError:
                write_log("Invalid authorization code.")
                exit()

    def __create_sevice(self):
        credentials = self.__google_authentication()
        service = build("calendar", "v3", credentials=credentials)
        return service

    def __save_calendar_id(self, id):
        with open(self.calendar_id_path, "w") as file:
            file.write(id)

    def __load_calendar_id(self):
        with open(self.calendar_id_path, "r") as file:
            return file.readline().strip()

    def __does_calendar_id_file_exist(self):
        if os.path.isfile(self.calendar_id_path) is True:
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
        write_log("Created new Calendar.", "Calendar-ID: " + calendar_id,
                  "Calendar-ID has been stored in " + self.calendar_id_path)
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
        event_id = event["id"]
        write_log("Event created.", "Event-ID: " + event_id)
        return event_id

    def delete_event(self, event_id):
        service = self.__create_sevice()
        calendar_id = self.__get_calendar_id()
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        write_log("Event deleted.", "Deleted-Event-ID: " + event_id)

    def update_event(self, event_id, new_title, new_start_time, new_end_time, new_description):
        self.delete_event(event_id)
        new_event_id = self.create_event(new_title, new_start_time, new_end_time, new_description)
        return new_event_id

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
        write_log("Crawling all events from the google calendar.")
        return calendar_events

    def turn_into_date_obj(self, date_str):
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")


calendar = Calendar()
