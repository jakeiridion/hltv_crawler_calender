from time import sleep
from GoogleCalendar import calendar
from HLTVCrawler import crawler
from Logger import write_log


class Application:
    def __add_events_to_calendar(self, events):
        for event in events:
            event_id = calendar.create_event(event.title, event.start_time, event.end_time, event.description)
            event.add_event_id(event_id)
        return events

    def __return_all_event_titles(self, events):
        titles = []
        for event in events:
            titles.append(event.title)
        return titles

    def __check_for_updates(self, events, previous_events):
        previous_events_titles = self.__return_all_event_titles(previous_events)

        for event in events:
            for previous_event in previous_events:
                if event.title == previous_event.title and (
                        event.start_time != previous_event.start_time or
                        event.end_time != previous_event.end_time or
                        event.description != previous_event.description):
                    calendar.update_event(
                        previous_event.event_id, event.title, event.start_time, event.end_time, event.description)
                    break

                elif event.title not in previous_events_titles:
                    calendar.create_event(event.title, event.start_time, event.end_time, event.description)
                    break

            continue

    def __first_run(self, events,  previous_events):
        if len(previous_events) == 0:
            self.__add_events_to_calendar(events)

    def run_app(self):
        while True:
            try:
                events = crawler.fetch_all_events()
                previous_events = calendar.fetch_events()
                self.__first_run(events, previous_events)
                self.__check_for_updates(events, previous_events)
                sleep(86400)

            except Exception as exception:
                sleep(1800)


if __name__ == "__main__":
    app = Application()
    app.run_app()
