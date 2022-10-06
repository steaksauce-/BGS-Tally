from os import path
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
        # Classes
        self.debug: Debug = Debug(self.plugin_name)
        self.state: State = State()
        self.mission_log: MissionLog = MissionLog(plugin_dir)
        self.discord: Discord = Discord(self.state)
        self.tick: Tick = Tick(True)
        self.overlay = Overlay()
        self.activity_manager: ActivityManager = ActivityManager(plugin_dir, self.mission_log, self.tick)
        self.ui: UI = UI(plugin_dir, self.state, self.activity_manager, self.tick, self.discord, self.overlay, self.version)


    def plugin_stop(self):
        """
        The plugin is shutting down.
        """
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


    def save_data(self):
        """
        Save all data structures
        """
        self.mission_log.save()
        self.tick.save()
        self.activity_manager.save()
        self.state.save()
