from threading import Thread
from time import sleep
from typing import Optional
from bgstally.enums import UpdateUIPolicy

import plug
import requests

from bgstally.activitymanager import ActivityManager
from bgstally.debug import Debug
from bgstally.discord import Discord
from bgstally.missionlog import MissionLog
from bgstally.overlay import Overlay
from bgstally.state import State
from bgstally.tick import Tick
from bgstally.ui import UI

PLUGIN_VERSION_URL = "https://api.github.com/repos/aussig/BGS-Tally/releases/latest"
TIME_WORKER_PERIOD_S = 60


class BGSTally:
    """
    Main plugin class
    """
    def __init__(self, plugin_name: str, version:str):
        self.plugin_name:str = plugin_name
        self.version:str = version
        self.git_version:str = "0.0.0"


    def plugin_start(self, plugin_dir: str):
        """
        The plugin is starting up. Initialise all our objects.
        """
        self.plugin_dir = plugin_dir

        # Classes
        self.debug: Debug = Debug(self)
        self.state: State = State(self)
        self.mission_log: MissionLog = MissionLog(self)
        self.discord: Discord = Discord(self)
        self.tick: Tick = Tick(self, True)
        self.overlay = Overlay(self)
        self.activity_manager: ActivityManager = ActivityManager(self)
        self.ui: UI = UI(self)

        self.shutting_down: bool = False

        self.thread: Optional[Thread] = Thread(target=self._worker, name="BGSTally Main worker")
        self.thread.daemon = True
        self.thread.start()


    def plugin_stop(self):
        """
        The plugin is shutting down.
        """
        self.shutting_down = True
        self.ui.shut_down()
        self.save_data()


    def check_version(self):
        """
        Check for a new plugin version
        """
        try:
            response = requests.get(PLUGIN_VERSION_URL, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.debug.logger.warning(f"Unable to fetch latest plugin version", exc_info=e)
            plug.show_error(f"BGS-Tally: Unable to fetch latest plugin version")
            return None
        else:
            latest = response.json()
            self.git_version = latest['tag_name']

        return True


    def check_tick(self, uipolicy: UpdateUIPolicy):
        """
        Check for a new tick
        """
        tick_success = self.tick.fetch_tick()

        if tick_success:
            self._new_tick(False, uipolicy)
            return True
        else:
            return tick_success


    def save_data(self):
        """
        Save all data structures
        """
        self.mission_log.save()
        self.tick.save()
        self.activity_manager.save()
        self.state.save()


    def _new_tick(self, force: bool, uipolicy: UpdateUIPolicy):
        """
        Start a new tick.
        """
        if force: self.tick.force_tick()
        self.activity_manager.new_tick(self.bgstally.tick)

        match uipolicy:
            case UpdateUIPolicy.IMMEDIATE:
                self.ui.update_plugin_frame()
            case UpdateUIPolicy.LATER:
                self.ui.frame_needs_updating = True

        self.overlay.display_message("tickwarn", f"NEW TICK DETECTED!", True, 180, "green")


    def _worker(self) -> None:
        """
        Handle thread work
        """
        Debug.logger.debug("Starting Main Worker...")

        while True:
            if self.shutting_down:
                Debug.logger.debug("Shutting down Main Worker...")
                return

            self.check_tick(UpdateUIPolicy.LATER) # Must not update UI directly from a thread

            sleep(TIME_WORKER_PERIOD_S)
