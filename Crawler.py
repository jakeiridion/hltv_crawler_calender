import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta
from time import sleep


class HLTV_Crawler:
    def __init__(self):
        self.__hltv_url = "https://www.hltv.org/events#tab-ALL"
        self.__join_url = "https://www.hltv.org"
        self.ongoing_events = []
        self.upcoming_events = []

    def __fetch_soup(self):
        r = requests.get(self.__hltv_url)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup

    def __add_year_to_date_string(self, date_str):
        date = str(date_str).split(" ")
        if len(date) > 3:
            date.insert(2, date[-1])

        return " ".join(date)

    def __replace_date(self, date_str):
        date = self.__add_year_to_date_string(date_str)
        date = date.replace("th", "")
        date = date.replace("nd", "")
        date = date.replace("rd", "")
        date = date.replace("st", "")
        return date

    def __turn_into_date_obj(self, date_str):
        entire_date = self.__replace_date(date_str)
        dates = entire_date.split(" - ")

        if len(dates) == 1:
            start_date = datetime.strptime(dates[0], "%b %d %Y")
            end_date = start_date + timedelta(days=1)
            return start_date, end_date

        else:
            start_date = datetime.strptime(dates[0], "%b %d %Y")
            end_date = datetime.strptime(dates[1], "%b %d %Y")
            return start_date, end_date

    def __fetch_ongoing_event(self, event_in_list):
        table = event_in_list.find_next("table")

        event_link = urljoin(self.__join_url, event_in_list["href"])
        event_name = table.find_next("div", attrs={"class": "text-ellipsis"}).text

        r = requests.get(event_link)
        link_soup = BeautifulSoup(r.text, "html.parser")
        event_date_str = link_soup.find("td", attrs={"class": "eventdate"}).text
        event_start_date, event_end_date = self.__turn_into_date_obj(event_date_str)

        self.ongoing_events.append([event_name, event_start_date, event_end_date, event_link])

    def fetch_ongoing_events(self):
        self.ongoing_events = []
        soup = self.__fetch_soup()

        for event in soup.find("div", attrs={"id": "ALL"}).find_all_next("a", attrs={"class": "a-reset ongoing-event"}):
            self.__fetch_ongoing_event(event)
            sleep(0.5)

    def __fetch_upcoming_months(self):
        soup = self.__fetch_soup()
        months = soup.find_all("div", attrs={"class": "events-month"})
        return months

    def fetch_upcoming_events(self):
        self.upcoming_events = []
        months = self.__fetch_upcoming_months()
        for month in months:
            date_year = str(month.find("div", attrs={"class": "standard-headline"}).text).split(" ").pop()
            for event in month.find_all("a"):

                try:
                    event_name = event.find("div", attrs={"class": "text-ellipsis"}).text
                    event_date = self.__turn_into_date_obj(event.find_all("span")[2].text + " " + date_year)
                except AttributeError:
                    event_name = event.find("div", attrs={"class": "big-event-name"}).text
                    event_date = self.__turn_into_date_obj(event.find("td", attrs={"class": "col-value col-date"}).text + " " + date_year)

                event_link = urljoin(self.__join_url, event["href"])

                self.upcoming_events.append([event_name, event_date, event_link])


crawler = HLTV_Crawler()
crawler.fetch_ongoing_events()
crawler.fetch_upcoming_events()

for i in crawler.ongoing_events:
    print(i)

print()

for i in crawler.upcoming_events:
    print(i)
