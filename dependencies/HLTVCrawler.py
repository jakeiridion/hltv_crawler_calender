import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta
from time import sleep
from dependencies.Logger import write_log
from dependencies.ConfigReader import config


# A crawled event object
class CrawledEvent:
    def __init__(self, title, start_time, end_time, description, event_id=None):
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
        self.event_id = event_id


# The crawler
class HLTV_Crawler:
    def __init__(self):
        self.__hltv_url = "https://www.hltv.org/events#tab-ALL"
        self.__join_url = "https://www.hltv.org"
        self.__headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
        self.__timezone = config.timezone

    # returns the hltv events website as a soup
    def __fetch_soup(self):
        r = requests.get(self.__hltv_url, headers=self.__headers)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup

    # Because the crawled date string looks like this: Mar 19th - Mar 21st 2020
    # I needed to add the year to the previous one. Like this: Mar 19th 2020 - Mar 21st 2020
    def __add_year_to_date_string(self, date_str):
        date = str(date_str).split(" ")
        if len(date) > 3:
            date.insert(2, date[-1])
        return " ".join(date)

    # removes the appendix to the date: 19th -> 19 for example
    def __replace_date(self, date_str):
        date = self.__add_year_to_date_string(date_str)
        date = date.replace("th", "")
        date = date.replace("nd", "")
        date = date.replace("rd", "")
        date = date.replace("st", "")
        return date

    # creates a datetime object with the previously formatted string.
    def __turn_into_date_obj(self, date_str):
        entire_date = self.__replace_date(date_str)
        dates = entire_date.split(" - ")

        if len(dates) == 1:
            start_date = self.__timezone.localize(datetime.strptime(dates[0], "%b %d %Y"))
            end_date = start_date + timedelta(days=1)
            return start_date, end_date

        else:
            start_date = self.__timezone.localize(datetime.strptime(dates[0], "%b %d %Y"))
            end_date = self.__timezone.localize(datetime.strptime(dates[1], "%b %d %Y"))
            return start_date, end_date

    # fetches a single ongoing event from a event list
    def __fetch_ongoing_event(self, event_in_list):
        table = event_in_list.find_next("table")

        event_link = urljoin(self.__join_url, event_in_list["href"])
        event_name = table.find_next("div", attrs={"class": "text-ellipsis"}).text

        r = requests.get(event_link, headers=self.__headers)
        link_soup = BeautifulSoup(r.text, "html.parser")
        event_date_str = link_soup.find("td", attrs={"class": "eventdate"}).text
        start_time, ent_time = self.__turn_into_date_obj(event_date_str)

        return CrawledEvent(event_name, start_time, ent_time, event_link)

    # fetches all ongoing events
    def fetch_ongoing_events(self):
        ongoing_events = []
        soup = self.__fetch_soup()
        events = soup.find("div", attrs={"id": "ALL"}).find_all_next("a", attrs={"class": "a-reset ongoing-event"})
        for event in events:
            ongoing_events.append(self.__fetch_ongoing_event(event))
            sleep(0.5)
        return ongoing_events

    # fetches the months section in the soup containing all the upcoming events
    def __fetch_upcoming_months(self):
        soup = self.__fetch_soup()
        months = soup.find_all("div", attrs={"class": "events-month"})
        return months

    # fetch all upcoming events
    def fetch_upcoming_events(self):
        upcoming_events = []
        months = self.__fetch_upcoming_months()
        for month in months:
            date_year = str(month.find("div", attrs={"class": "standard-headline"}).text).split(" ").pop()
            for event in month.find_all("a"):

                try:
                    event_name = event.find("div", attrs={"class": "text-ellipsis"}).text
                    event_date = self.__turn_into_date_obj(event.find_all("span")[2].text + " " + date_year)
                except AttributeError:
                    event_name = event.find("div", attrs={"class": "big-event-name"}).text
                    event_date = self.__turn_into_date_obj(
                        event.find("td", attrs={"class": "col-value col-date"}).text + " " + date_year)

                start_time, end_time = event_date
                event_link = urljoin(self.__join_url, event["href"])

                upcoming_events.append(CrawledEvent(event_name, start_time, end_time, event_link))
        return upcoming_events

    # returns the ongoing and upcoming events
    def fetch_all_events(self):
        write_log("Crawling all events from hltv.org/events.")
        return self.fetch_ongoing_events() + self.fetch_upcoming_events()


crawler = HLTV_Crawler()
