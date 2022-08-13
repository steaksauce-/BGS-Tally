import random
import string
from datetime import datetime

import plug
import requests

DATETIME_FORMAT_ELITEBGS = "%Y-%m-%dT%H:%M:%S.%fZ"
DATETIME_FORMAT_DISPLAY = "%Y-%m-%d %H:%M:%S"

class Tick:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.tick_id = ""
        self.tick_time = ""
        self.load()


    def fetch_tick(self):
        """
        Tick check and counter reset
        """
        try:
            response = requests.get('https://elitebgs.app/api/ebgs/v5/ticks', timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Unable to fetch latest tick from elitebgs.app", exc_info=e)
            plug.show_error(f"BGS-Tally: Unable to fetch latest tick from elitebgs.app")
            return None
        else:
            tick = response.json()

            if self.tick_id != tick[0]['_id']:
                # There is a new tick ID
                self.tick_id = tick[0]['_id']
                self.tick_time = tick[0]['time']
                return True

        return False


    def force_tick(self):
        """
        Force a new tick, user-initiated
        """
        # Keep the same tick ID so we don't start another new tick on next launch,
        # but update the time to show the user that something has happened
        self.tick_time = datetime.now().strftime(DATETIME_FORMAT_ELITEBGS)


    def load(self):
        """
        Load tick status from config
        """
        self.tick_id = self.config.get_str("XLastTick")
        self.tick_time = self.config.get_str("XTickTime")


    def save(self):
        """
        Save tick status to config
        """
        self.config.set('XLastTick', self.tick_id)
        self.config.set('XTickTime', self.tick_time)


    def get_formatted(self):
        """
        Return a formatted tick date/time
        """
        datetime_object = datetime.strptime(self.tick_time, DATETIME_FORMAT_ELITEBGS)
        return datetime_object.strftime(DATETIME_FORMAT_DISPLAY)
