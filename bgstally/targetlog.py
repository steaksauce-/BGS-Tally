import json
import re
import os.path
from typing import Dict
from datetime import datetime, timedelta

from bgstally.constants import DATETIME_FORMAT_JOURNAL
from bgstally.debug import Debug

FILENAME = "targetlog.json"
TIME_TARGET_LOG_EXPIRY_D = 30


class TargetLog:
    """
    Handle a log of all targeted players
    """
    cmdr_name_pattern:re.Pattern = re.compile(r"\$cmdr_decorate\:#name=([^]]*);")

    def __init__(self, bgstally):
        self.bgstally = bgstally
        self.targetlog = []
        self.load()


    def load(self):
        """
        Load state from file
        """
        file = os.path.join(self.bgstally.plugin_dir, FILENAME)
        if os.path.exists(file):
            with open(file) as json_file:
                self.targetlog = json.load(json_file)

    def save(self):
        """
        Save state to file
        """
        file = os.path.join(self.bgstally.plugin_dir, FILENAME)
        with open(file, 'w') as outfile:
            json.dump(self.targetlog, outfile)


    def get_targetlog(self):
        """
        Get the current target log
        """
        return self.targetlog


    def ship_targeted(self, journal_entry: Dict, system: str):
        """
        A ship targeted event has been received, if it's a player, add it to the target log
        """
        # { "timestamp":"2022-10-09T06:49:06Z", "event":"ShipTargeted", "TargetLocked":true, "Ship":"cutter", "Ship_Localised":"Imperial Cutter", "ScanStage":3, "PilotName":"$cmdr_decorate:#name=[Name];", "PilotName_Localised":"[CMDR Name]", "PilotRank":"Elite", "SquadronID":"TSPA", "ShieldHealth":100.000000, "HullHealth":100.000000, "LegalStatus":"Clean" }
        if not 'ScanStage' in journal_entry or journal_entry['ScanStage'] < 3: return
        if not 'PilotName' in journal_entry or not journal_entry['PilotName'].startswith("$cmdr_decorate:#name"): return

        cmdr_match = self.cmdr_name_pattern.match(journal_entry['PilotName'])
        if not cmdr_match: return
        cmdr_name = cmdr_match.group(1)

        self.targetlog.append({'TargetName': cmdr_name,
                                'System': system,
                                'SquadronID': journal_entry['SquadronID'] if 'SquadronID' in journal_entry else "----",
                                'Ship': journal_entry['Ship_Localised'],
                                'LegalStatus': journal_entry['LegalStatus'],
                                'Timestamp': journal_entry['timestamp']})


    def _expire_old_targets(self):
        """
        Clear out all targets older than 7 days from the target log
        """
        for target in reversed(self.targetlog):
            timedifference = datetime.utcnow() - datetime.strptime(target['Timestamp'], DATETIME_FORMAT_JOURNAL)
            if timedifference > timedelta(days = TIME_TARGET_LOG_EXPIRY_D):
                self.targetlog.remove(target)
