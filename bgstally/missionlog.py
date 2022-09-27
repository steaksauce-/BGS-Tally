import json
import os.path
from datetime import datetime, timedelta

from bgstally.debug import Debug

DATETIME_FORMAT_JOURNAL = "%Y-%m-%dT%H:%M:%SZ"

class MissionLog:
    def __init__(self, plugindir: str):
        self.plugindir = plugindir
        self.missionlog = []
        self.load()


    def load(self):
        """
        Load missionlog status from file
        """
        file = os.path.join(self.plugindir, "MissionLog.txt")
        if os.path.exists(file):
            with open(file) as json_file:
                self.missionlog = json.load(json_file)

    def save(self):
        """
        Save missionlog to file
        """
        file = os.path.join(self.plugindir, "MissionLog.txt")
        with open(file, 'w') as outfile:
            json.dump(self.missionlog, outfile)


    def get_missionlog(self):
        """
        Get the current missionlog
        """
        return self.missionlog


    def add_mission(self, name: str, faction: str, missionid: str, expiry: str, system_name: str):
        """
        Add a mission to the missionlog
        """
        self.missionlog.append({"Name": name, "Faction": faction, "MissionID": missionid, "Expiry": expiry, "System": system_name})


    def delete_mission_by_id(self, missionid: str):
        """
        Delete the mission with the given id from the missionlog
        """
        for i in range(len(self.missionlog)):
            if self.missionlog[i]["MissionID"] == missionid:
                self.missionlog.pop(i)
                break


    def delete_mission_by_index(self, missionindex: int):
        """
        Delete the mission at the given index from the missionlog
        """
        self.missionlog.pop(missionindex)


    def get_active_systems(self):
        """
        Return a list of systems that have currently active missions
        """
        systems = [x['System'] for x in self.missionlog]
        # De-dupe before returning
        return list(dict.fromkeys(systems))


    def _expire_old_missions(self):
        """
        Clear out all missions older than 7 days from the mission log
        """
        for mission in reversed(self.missionlog):
            # Old missions pre v1.11.0 don't have Expiry stored. Set to 7 days ahead for safety
            if not "Expiry" in mission: mission["Expiry"] = (datetime.utcnow() + timedelta(days = 7)).strftime(DATETIME_FORMAT_JOURNAL)

            timedifference = datetime.utcnow() - datetime.strptime(mission["Expiry"], DATETIME_FORMAT_JOURNAL)
            if timedifference > timedelta(days=7):
                # Keep missions for a while after they have expired, so we can log failed missions correctly
                self.missionlog.remove(mission)
