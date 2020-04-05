from time import sleep
from dependencies.GoogleCalendar import calendar
from dependencies.HLTVCrawler import crawler
from dependencies.Logger import write_log
from dependencies.ConfigReader import config


class Application:
    def __add_events_to_calendar(self, events):
        for event in events:
            calendar.create_event(event.title, event.start_time, event.end_time, event.description)

    def __return_all_event_titles(self, events):
        titles = []
        for event in events:
            titles.append(event.title)
        return titles

    def __check_for_updates(self, events, previous_events):
        write_log("Checking for updates.")
        previous_events_titles = self.__return_all_event_titles(previous_events)

        for event in events:
            for previous_event in previous_events:
                if event.title == previous_event.title and (
                        event.start_time != previous_event.start_time or
                        event.end_time != previous_event.end_time or
                        event.description != previous_event.description):
                    write_log("Update detected.")
                    calendar.update_event(
                        previous_event.event_id, event.title, event.start_time, event.end_time, event.description)
                    break

                elif event.title not in previous_events_titles:
                    write_log("New event detected.")
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
                write_log("Application continues in " + str(config.wait_between_check) + " Seconds.")
                sleep(config.wait_between_check)

            except KeyboardInterrupt:
                break

            except Exception as exception:
                write_log("An Error occurred:", exception,
                          "Application continues in " + str(config.wait_between_error) + " Seconds.")
                try:
                    sleep(config.wait_between_error)

                except KeyboardInterrupt:
                    break


if __name__ == "__main__":
    app = Application()
    write_log("Application started.")
    app.run_app()
    write_log("Application terminated.")
