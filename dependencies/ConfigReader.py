import configparser
import os
from pytz import timezone
from dependencies.Logger import write_log


class Config:
    def __init__(self):
        try:
            # import Variables from the settings file
            cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "SETTINGS.ini")
            cfg = configparser.ConfigParser()
            cfg.read(cfg_path)

            self.client_secret_path = str(cfg.get("Settings", "client_secret.json_path"))
            self.timezone = timezone(str(cfg.get("Settings", "timezone")))
            self.wait_between_check = int(cfg.get("Settings", "wait_between_check"))
            self.wait_between_error = int(cfg.get("Settings", "wait_between_error"))

            if os.path.isfile(self.client_secret_path) is False:
                raise Exception("No such file or directory: " + self.client_secret_path)

        except Exception as exception:
            write_log("An Error Occurred with your Settings", exception)
            exit()


config = Config()
