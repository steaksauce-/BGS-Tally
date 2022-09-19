import imp
import json

from bgstally.debug import Debug
from bgstally.tick import Tick


class Activity:
    """
    A single tick of user activity

    Activity is stored in the self.data Dict, with key = SystemAddress and value = Dict containing the system name and a List of
    factions with their activity
    """

    def __init__(self, plugindir, tick = None):
        """
        Instantiate using a given tickid
        """
        if tick == None: tick = Tick()
        self.tickid = tick.tickid
        self.ticktime = tick.ticktime
        self.plugindir = plugindir
        self.data = {'tickid': self.tickid, 'ticktime': self.ticktime, 'systems': {}}


    def load(self, filepath):
        """
        Load an activity file
        """
        with open(filepath) as activityfile:
            self.data = json.load(activityfile)
            self.tickid = self.data.get('tickid')
            self.ticktime = self.data.get('ticktime')


    def save(self, filepath):
        """
        Save to an activity file
        """
        with open(filepath, 'w') as activityfile:
            json.dump(self.data, activityfile)


    def load_legacy_data(self, filepath):
        """
        Load and populate from a legacy (v1) data structure - i.e. the old Today Data.txt and Yesterday Data.txt files
        """
        # Convert:
        # {"1": [{"System": "Sowiio", "SystemAddress": 1458376217306, "Factions": [{}, {}], "zero_system_activity": false}]}
        # To:
        # {"tickid": tickid, "ticktime": ticktime, "systems": {1458376217306: {"System": "Sowiio", "SystemAddress": 1458376217306, "Factions": [{}, {}], "zero_system_activity": false}}}
        with open(filepath) as legacyactivityfile:
            legacydata = json.load(legacyactivityfile)
            for legacysystemlist in legacydata.values():  # Iterate the values of the dict. We don't care about the keys - they were just "1", "2" etc.
                legacysystem = legacysystemlist[0] # For some reason each system was a list, but always had just 1 entry
                if 'SystemAddress' in legacysystem:
                    self.data['systems'][legacysystem['SystemAddress']] = legacysystem # Copy entire existing data structure in, we don't change it inside the system
