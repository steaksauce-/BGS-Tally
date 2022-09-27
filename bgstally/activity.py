import json
from datetime import datetime
from typing import Any, Dict

from bgstally.debug import Debug
from bgstally.enums import CheckStates
from bgstally.missionlog import MissionLog
from bgstally.tick import Tick

DATETIME_FORMAT_ACTIVITY = "%Y-%m-%dT%H:%M:%S.%fZ"
CONFLICT_STATES = ['War', 'CivilWar']
ELECTION_STATES = ['Election']

# Missions that we count as +1 INF in Elections even if the Journal reports no +INF
ELECTION_MISSIONS = [
    'Mission_AltruismCredits_name',
    'Mission_Collect_name', 'Mission_Collect_Industrial_name',
    'Mission_Courier_name', 'Mission_Courier_Boom_name', 'Mission_Courier_Democracy_name', 'Mission_Courier_Elections_name', 'Mission_Courier_Expansion_name',
    'Mission_Delivery_name', 'Mission_Delivery_Agriculture_name', 'Mission_Delivery_Boom_name', 'Mission_Delivery_Confederacy_name', 'Mission_Delivery_Democracy_name',
    'Mission_Mining_name', 'Mission_Mining_Boom_name', 'Mission_Mining_Expansion_name',
    'Mission_OnFoot_Collect_MB_name',
    'Mission_OnFoot_Salvage_MB_name', 'Mission_OnFoot_Salvage_BS_MB_name',
    'Mission_PassengerBulk_name', 'Mission_PassengerBulk_AIDWORKER_ARRIVING_name', 'Mission_PassengerBulk_BUSINESS_ARRIVING_name', 'Mission_PassengerBulk_POLITICIAN_ARRIVING_name', 'Mission_PassengerBulk_SECURITY_ARRIVING_name',
    'Mission_PassengerVIP_name', 'Mission_PassengerVIP_CEO_BOOM_name', 'Mission_PassengerVIP_CEO_EXPANSION_name', 'Mission_PassengerVIP_Explorer_EXPANSION_name', 'Mission_PassengerVIP_Tourist_ELECTION_name', 'Mission_PassengerVIP_Tourist_BOOM_name',
    'Mission_Rescue_Elections_name',
    'Mission_Salvage_name', 'Mission_Salvage_Planet_name', 'MISSION_Salvage_Refinery_name',
    'MISSION_Scan_name',
    'Mission_Sightseeing_name', 'Mission_Sightseeing_Celebrity_ELECTION_name', 'Mission_Sightseeing_Tourist_BOOM_name',
    'Chain_HelpFinishTheOrder_name'
]

# Missions that we count as +1 INF in conflicts even if the Journal reports no +INF
CONFLICT_MISSIONS = [
    'Mission_Assassinate_Legal_CivilWar_name', 'Mission_Assassinate_Legal_War_name',
    'Mission_Massacre_Conflict_CivilWar_name', 'Mission_Massacre_Conflict_War_name',
    'Mission_OnFoot_Assassination_Covert_MB_name',
    'Mission_OnFoot_Onslaught_Offline_MB_name'
]


class Activity:
    """
    User activity for a single tick

    Activity is stored in the self.systems Dict, with key = SystemAddress and value = Dict containing the system name and a Dict of
    factions with their activity
    """

    def __init__(self, plugindir: str, tick: Tick = None, discord_messageid: str = None):
        """
        Instantiate using a given Tick
        """
        if tick == None: tick = Tick()

        # Stored data
        self.tick_id = tick.tick_id
        self.tick_time = tick.tick_time
        self.discord_messageid = discord_messageid
        self.systems = {}

        # Transient data
        self.plugindir = plugindir
        self.current_system = None


    def entered_system(self, log_entry: Dict[str, Any]):
        """
        The user has entered a system
        """
        try: test = log_entry['Factions']
        except KeyError: return

        for system_address in self.systems:
            if system_address == log_entry['SystemAddress']:
                # We already have an entry for this system
                self.current_system = self.systems[system_address]
                break

        if self.current_system is None:
            # We don't have this system yet
            self.current_system = self._get_new_system_data(log_entry['StarSystem'], log_entry['SystemAddress'], {})
            self.systems[log_entry['SystemAddress']] = self.current_system

        conflicts = 0

        # Iterate all factions first to calculate the number of conflicts - If there is just a single faction in conflict,
        # this is a game bug, we override faction state to "None" in this circumstance.
        # TODO: Ideally we could try to be cleverer and separately detect the number of elections, civil wars and wars, and if
        # any of these are == 1 then don't allow the faction to be in that state. Even cleverer, and if possible, it would be
        # great to 'pair up' the conflict factions and remove the state from ones that are not paired.
        for faction in log_entry['Factions']:
            if faction['Name'] == "Pilots' Federation Local Branch": continue
            if faction['FactionState'] in CONFLICT_STATES or faction['FactionState'] in ELECTION_STATES: conflicts += 1

        for faction in log_entry['Factions']:
            if faction['Name'] == "Pilots' Federation Local Branch": continue

            if faction['Name'] in self.current_system['Factions']:
                # We have this faction, ensure it's up to date with latest state
                faction_data = self.current_system['Factions'][faction['Name']]
                self._update_faction_data(faction_data, faction['FactionState'] if conflicts != 1 else "None")
            else:
                # We do not have this faction, create a new clean entry
                self.current_system['Factions'][faction['Name']] = self._get_new_faction_data(faction['Name'], faction['FactionState'] if conflicts != 1 else "None")


    def load_legacy_data(self, filepath: str):
        """
        Load and populate from a legacy (v1) data structure - i.e. the old Today Data.txt and Yesterday Data.txt files
        """
        # Convert:
        # {"1": [{"System": "Sowiio", "SystemAddress": 1458376217306, "Factions": [{}, {}], "zero_system_activity": false}]}
        # To:
        # {"tick_id": tick_id, "tick_time": tick_time, "discord_messageid": discordmessageid, "systems": {1458376217306: {"System": "Sowiio", "SystemAddress": 1458376217306, "zero_system_activity": false, "Factions": {"Faction Name 1": {}, "Faction Name 2": {}}}}}
        with open(filepath) as legacyactivityfile:
            legacydata = json.load(legacyactivityfile)
            for legacysystemlist in legacydata.values():  # Iterate the values of the dict. We don't care about the keys - they were just "1", "2" etc.
                legacysystem = legacysystemlist[0]        # For some reason each system was a list, but always had just 1 entry
                if 'SystemAddress' in legacysystem:
                    # Build and convert system data
                    factions = {}
                    for faction in legacysystem['Factions']:
                        # Just convert List to Dict, with faction name as key
                        factions[faction['Faction']] = faction

                    self.systems[legacysystem['SystemAddress']] = self._get_new_system_data(legacysystem['System'], legacysystem['SystemAddress'], factions)


    def load(self, filepath: str):
        """
        Load an activity file
        """
        with open(filepath) as activityfile:
            self._from_dict(json.load(activityfile))
            self._recalculate_zero_activity()


    def save(self, filepath: str):
        """
        Save to an activity file
        """
        with open(filepath, 'w') as activityfile:
            json.dump(self._as_dict(), activityfile)


    def clear_activity(self, mission_log: MissionLog):
        """
        Clear down all activity. If there is a currently active mission in a system, only zero the activity,
        otherwise delete the system completely.
        """
        mission_systems = mission_log.get_active_systems()

        # Need to convert keys to list so we can delete as we iterate
        for system_address in list(self.systems.keys()):
            system = self.systems[system_address]
            # Note that the missions log historically stores system name so we check for that, not system address.
            # Potential for very rare bug here for systems with duplicate names.
            if system['System'] in mission_systems:
                # The system has a current mission, zero, don't delete
                for faction_name, faction_data in system['Factions'].items():
                    system['Factions'][faction_name] = self._get_new_faction_data(faction_name, faction_data['FactionState'])
            else:
                # No current missions, delete the whole system
                del self.systems[system_address]


    def _get_new_system_data(self, system_name: str, system_address: str, faction_data: Dict):
        """
        Get a new data structure for storing system data
        """
        return {'System': system_name,
                'SystemAddress': system_address,
                'Factions': faction_data}


    def _get_new_faction_data(self, faction_name, faction_state):
        """
        Get a new data structure for storing faction data
        """
        return {'Faction': faction_name, 'FactionState': faction_state, 'Enabled': CheckStates.STATE_ON,
                'MissionPoints': 0, 'MissionPointsSecondary': 0,
                'TradeProfit': 0, 'TradePurchase': 0, 'BlackMarketProfit': 0, 'Bounties': 0, 'CartData': 0, 'ExoData': 0,
                'CombatBonds': 0, 'MissionFailed': 0, 'Murdered': 0,
                'SpaceCZ': {}, 'GroundCZ': {}, 'GroundCZSettlements': {}, 'Scenarios': 0}


    def _update_faction_data(self, faction_data: Dict, faction_state: str = None):
        """
        Update faction data structure for elements not present in previous versions of plugin
        """
        # Update faction state as it can change at any time post-tick
        if faction_state: faction_data['FactionState'] = faction_state

        # From < v1.2.0 to 1.2.0
        if not 'SpaceCZ' in faction_data: faction_data['SpaceCZ'] = {}
        if not 'GroundCZ' in faction_data: faction_data['GroundCZ'] = {}
        # From < v1.3.0 to 1.3.0
        if not 'Enabled' in faction_data: faction_data['Enabled'] = CheckStates.STATE_ON
        # From < v1.6.0 to 1.6.0
        if not 'MissionPointsSecondary' in faction_data: faction_data['MissionPointsSecondary'] = 0
        # From < v1.7.0 to 1.7.0
        if not 'ExoData' in faction_data: faction_data['ExoData'] = 0
        if not 'GroundCZSettlements' in faction_data: faction_data['GroundCZSettlements'] = {}
        # From < v1.8.0 to 1.8.0
        if not 'BlackMarketProfit' in faction_data: faction_data['BlackMarketProfit'] = 0
        if not 'TradePurchase' in faction_data: faction_data['TradePurchase'] = 0
        # From < v1.9.0 to 1.9.0
        if not 'Scenarios' in faction_data: faction_data['Scenarios'] = 0


    def _recalculate_zero_activity(self):
        """
        For efficiency, we store whether each system has had any activity in the data structure
        """
        for system in self.systems.values():
            system['zero_system_activity'] = True
            for faction_data in system['Factions'].values():
                self._update_faction_data(faction_data)
                if not self._is_faction_data_zero(faction_data):
                    system['zero_system_activity'] = False
                    break


    def _is_faction_data_zero(self, faction_data: Dict):
        """
        Check whether all information is empty or zero for a faction
        """
        return faction_data['MissionPoints'] == 0 and faction_data['MissionPointsSecondary'] == 0 and \
                faction_data['TradeProfit'] == 0 and faction_data['TradePurchase'] == 0 and faction_data['BlackMarketProfit'] == 0 and \
                faction_data['Bounties'] == 0 and faction_data['CartData'] == 0 and faction_data['ExoData'] == 0 and \
                faction_data['CombatBonds'] == 0 and faction_data['MissionFailed'] == 0 and faction_data['Murdered'] == 0 and \
                faction_data['SpaceCZ'] == {} and faction_data['GroundCZ'] == {} and faction_data['GroundCZSettlements'] == {} and \
                faction_data['Scenarios'] == 0


    def _as_dict(self):
        """
        Return a Dictionary representation of our data, suitable for serializing
        """
        return {
            'tickid': self.tick_id,
            'ticktime': self.tick_time.strftime(DATETIME_FORMAT_ACTIVITY),
            'discordmessageid': self.discord_messageid,
            'systems': self.systems}


    def _from_dict(self, dict: Dict):
        """
        Populate our data from a Dictionary that has been deserialized
        """
        self.tick_id = dict.get('tickid')
        self.tick_time = datetime.strptime(dict.get('ticktime'), DATETIME_FORMAT_ACTIVITY)
        self.discord_messageid = dict.get('discordmessageid')
        self.systems = dict.get('systems')



    # Comparator functions - we use the tick_time for sorting

    def __eq__(self, other):
        if isinstance(other, Activity): return (self.tick_time == other.tick_time)
        return False

    def __lt__(self, other):
        if isinstance(other, Activity): return (self.tick_time < other.tick_time)
        return False

    def __le__(self, other):
        if isinstance(other, Activity): return (self.tick_time <= other.tick_time)
        return False

    def __gt__(self, other):
        if isinstance(other, Activity): return (self.tick_time > other.tick_time)
        return False

    def __ge__(self, other):
        if isinstance(other, Activity): return (self.tick_time >= other.tick_time)
        return False

    def __repr__(self):
        return f"{self.tick_id} ({self.tick_time}): {self._as_dict()}"
