from datetime import datetime, timedelta

import plug
import requests
from config import config

from bgstally.debug import Debug

DATETIME_FORMAT_ELITEBGS = "%Y-%m-%dT%H:%M:%S.%fZ"
DATETIME_FORMAT_DISPLAY = "%Y-%m-%d %H:%M:%S"
TICKID_UNKNOWN = "unknown_tickid"


class Tick:
    def __init__(self, load = False):
        self.tickid = TICKID_UNKNOWN
        self.ticktime = (datetime.utcnow() - timedelta(days = 30)) # Default to a tick a month old
        if load: self.load()


    def fetch_tick(self):
        """
        Tick check and counter reset
        """
        try:
            response = requests.get('https://elitebgs.app/api/ebgs/v5/ticks', timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            Debug.logger.error(f"Unable to fetch latest tick from elitebgs.app", exc_info=e)
            plug.show_error(f"BGS-Tally: Unable to fetch latest tick from elitebgs.app")
            return None
        else:
            tick = response.json()

            if self.tickid != tick[0]['_id']:
                # There is a new tick ID
                self.tickid = tick[0]['_id']
                self.ticktime = datetime.strptime(tick[0]['time'], DATETIME_FORMAT_ELITEBGS)
                return True

        return False


    def force_tick(self):
        """
        Force a new tick, user-initiated
        """
        # Keep the same tick ID so we don't start another new tick on next launch,
        # but update the time to show the user that something has happened
        self.ticktime = datetime.now()


    def load(self):
        """
        Load tick status from config
        """
        self.tickid = config.get_str("XLastTick")
        self.ticktime = datetime.strptime(config.get_str("XTickTime"), DATETIME_FORMAT_ELITEBGS)


    def save(self):
        """
        Save tick status to config
        """
        config.set('XLastTick', self.tickid)
        config.set('XTickTime', self.ticktime.strftime(DATETIME_FORMAT_ELITEBGS))


    def get_formatted(self):
        """
        Return a formatted tick date/time
        """
        return self.ticktime.strftime(DATETIME_FORMAT_DISPLAY)
