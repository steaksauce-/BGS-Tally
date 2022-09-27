import copy
import sys
import tkinter as tk
from datetime import datetime, timedelta
from os import path

import plug
import requests
from theme import theme

from bgstally.activity import Activity
from bgstally.activitymanager import ActivityManager
from bgstally.debug import Debug
from bgstally.discord import Discord
from bgstally.enums import CheckStates
from bgstally.missionlog import MissionLog
from bgstally.prefs import Prefs
#from bgstally.overlay import Overlay
from bgstally.tick import Tick
from bgstally.ui import UI

plugin_name = path.basename(path.dirname(__file__))

this = sys.modules[__name__]  # For holding module globals
this.VersionNo = "1.10.0"
this.GitVersion = "0.0.0"
this.DataIndex = 0
this.LastSettlementApproached = {}
this.LastShipTargeted = {}


def plugin_start3(plugin_dir):
    """
    Load this plugin into EDMC
    """

    # Classes
    this.debug = Debug(plugin_name)
    this.prefs = Prefs()
    this.mission_log = MissionLog(plugin_dir)
    this.discord = Discord(this.prefs)
    #this.overlay = Overlay()
    this.tick = Tick(True)
    this.activity_manager = ActivityManager(plugin_dir, this.mission_log, this.tick)
    this.ui = UI(this.prefs, this.activity_manager, this.tick, this.discord, this.VersionNo)

    version_success = check_version()
    tick_success = this.tick.fetch_tick()

    if tick_success == None:
        # Cannot continue if we couldn't fetch a tick
        raise Exception("BGS-Tally couldn't continue because the current tick could not be fetched")
    elif tick_success == True:
        this.ui.new_tick(False, False)

    #this.overlay.display_message("tickwarn", f"Tick: {this.tick.get_formatted()}")

    return plugin_name


def plugin_stop():
    """
    EDMC is closing
    """
    save_data()


def plugin_app(parent):
    """
    Return a TK Frame for adding to the EDMC main window
    """
    return this.ui.get_plugin_frame(parent, this.GitVersion)


def plugin_prefs(parent, cmdr, is_beta):
    """
    Return a TK Frame for adding to the EDMC settings dialog
    """
    return this.ui.get_prefs_frame(parent)


def check_version():
    """
    Check for a new plugin version
    """
    try:
        response = requests.get('https://api.github.com/repos/aussig/BGS-Tally/releases/latest', timeout=10)  # check latest version
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        this.debug.logger.warning(f"Unable to fetch latest plugin version", exc_info=e)
        plug.show_error(f"BGS-Tally: Unable to fetch latest plugin version")
        return None
    else:
        latest = response.json()
        this.GitVersion = latest['tag_name']

    return True


def journal_entry(cmdr, is_beta, system, station, entry, state):
    """
    Parse an incoming journal entry and store the data we need
    """
    if this.prefs.Status.get() != "Active": return

    if entry['event'] in ['Location', 'FSDJump', 'CarrierJump']:  # get factions and populate today data
        # Check for a new tick
        if this.tick.fetch_tick(): this.ui.new_tick(False, True)

        activity = this.activity_manager.get_current_activity()
        activity.entered_system(entry)


    if entry['event'] == 'Docked':  # enter system and faction named
        this.StationFaction.set(entry['StationFaction']['Name'])  # set controlling faction name
        this.StationType.set(entry['StationType'])  # set docked station type

    if (entry['event'] == 'Location' or entry['event'] == 'StartUp') and entry['Docked'] == True:
        this.StationType.set(entry['StationType'])  # set docked station type

    if entry['event'] == 'MissionCompleted':  # get mission influence value
        fe = entry['FactionEffects']
        for i in fe:
            fe3 = i['Faction']
            if i['Influence'] != []:
                fe6 = i['Influence'][0]['SystemAddress']
                inf = len(i['Influence'][0]['Influence'])
                inftrend = i['Influence'][0]['Trend']
                for y in this.TodayData:
                    if fe6 == this.TodayData[y][0]['SystemAddress']:
                        t = len(this.TodayData[y][0]['Factions'])
                        for z in range(0, t):
                            if fe3 == this.TodayData[y][0]['Factions'][z]['Faction']:
                                if inftrend == "UpGood" or inftrend == "DownGood":
                                    if fe3 == entry['Faction']:
                                        this.TodayData[y][0]['Factions'][z]['MissionPoints'] += inf
                                    else:
                                        this.TodayData[y][0]['Factions'][z]['MissionPointsSecondary'] += inf
                                else:
                                    if fe3 == entry['Faction']:
                                        this.TodayData[y][0]['Factions'][z]['MissionPoints'] -= inf
                                    else:
                                        this.TodayData[y][0]['Factions'][z]['MissionPointsSecondary'] -= inf
            else:
                mission_log = this.mission_log.get_missionlog()
                for p in range(len(mission_log)):
                    if mission_log[p]["MissionID"] == entry["MissionID"]:
                        for y in this.TodayData:
                            if mission_log[p]['System'] == this.TodayData[y][0]['System']:
                                for z in range(0, len(this.TodayData[y][0]['Factions'])):
                                    if this.TodayData[y][0]['Factions'][z]['Faction'] == fe3:
                                        if (this.TodayData[y][0]['Factions'][z]['FactionState'] == 'Election' and entry['Name'] in Activity.ELECTION_MISSIONS) \
                                        or (this.TodayData[y][0]['Factions'][z]['FactionState'] in Activity.CONFLICT_STATES and entry['Name'] in Activity.CONFLICT_MISSIONS) \
                                            and fe3 == entry['Faction']:
                                                this.TodayData[y][0]['Factions'][z]['MissionPoints'] += 1
        this.mission_log.delete_mission_by_id(entry["MissionID"])
        save_data()

    if entry['event'] == 'SellExplorationData' or entry['event'] == "MultiSellExplorationData":  # get carto data value
        t = len(this.TodayData[this.DataIndex.get()][0]['Factions'])
        for z in range(0, t):
            if this.StationFaction.get() == this.TodayData[this.DataIndex.get()][0]['Factions'][z]['Faction']:
                this.TodayData[this.DataIndex.get()][0]['Factions'][z]['CartData'] += entry['TotalEarnings']
        save_data()

    if entry['event'] == 'SellOrganicData':  # get exobiology data value
        t = len(this.TodayData[this.DataIndex.get()][0]['Factions'])
        for z in range(0, t):
            if this.StationFaction.get() == this.TodayData[this.DataIndex.get()][0]['Factions'][z]['Faction']:
                for e in entry['BioData']:
                    this.TodayData[this.DataIndex.get()][0]['Factions'][z]['ExoData'] += e['Value'] + e['Bonus']
        save_data()

    if entry['event'] == 'RedeemVoucher' and entry['Type'] == 'bounty':  # bounties collected
        t = len(this.TodayData[this.DataIndex.get()][0]['Factions'])
        for z in entry['Factions']:
            for x in range(0, t):
                if z['Faction'] == this.TodayData[this.DataIndex.get()][0]['Factions'][x]['Faction']:
                    if this.StationType.get() == 'FleetCarrier':
                        this.TodayData[this.DataIndex.get()][0]['Factions'][x]['Bounties'] += (z['Amount'] / 2)
                    else:
                        this.TodayData[this.DataIndex.get()][0]['Factions'][x]['Bounties'] += z['Amount']
        save_data()

    if entry['event'] == 'RedeemVoucher' and entry['Type'] == 'CombatBond':  # combat bonds collected
        t = len(this.TodayData[this.DataIndex.get()][0]['Factions'])
        for x in range(0, t):
            if entry['Faction'] == this.TodayData[this.DataIndex.get()][0]['Factions'][x]['Faction']:
                this.TodayData[this.DataIndex.get()][0]['Factions'][x]['CombatBonds'] += entry['Amount']
        save_data()

    if entry['event'] == 'MarketBuy':  # Trade Purchase
        t = len(this.TodayData[this.DataIndex.get()][0]['Factions'])
        for z in range(0, t):
            if this.StationFaction.get() == this.TodayData[this.DataIndex.get()][0]['Factions'][z]['Faction']:
                this.TodayData[this.DataIndex.get()][0]['Factions'][z]['TradePurchase'] += entry['TotalCost']
        save_data()

    if entry['event'] == 'MarketSell':  # Trade Profit
        t = len(this.TodayData[this.DataIndex.get()][0]['Factions'])
        for z in range(0, t):
            if this.StationFaction.get() == this.TodayData[this.DataIndex.get()][0]['Factions'][z]['Faction']:
                cost = entry['Count'] * entry['AvgPricePaid']
                profit = entry['TotalSale'] - cost
                if 'BlackMarket' in entry and entry['BlackMarket'] == True:
                    this.TodayData[this.DataIndex.get()][0]['Factions'][z]['BlackMarketProfit'] += profit
                else:
                    this.TodayData[this.DataIndex.get()][0]['Factions'][z]['TradeProfit'] += profit
        save_data()

    if entry['event'] == 'MissionAccepted':  # mission accepted
        this.mission_log.add_mission(entry["Name"], entry["Faction"], entry["MissionID"], entry["Expiry"], system)
        save_data()

    if entry['event'] == 'MissionFailed':  # mission failed
        mission_log = this.mission_log.get_missionlog()
        for x in range(len(mission_log)):
            if mission_log[x]["MissionID"] == entry["MissionID"]:
                for y in this.TodayData:
                    if mission_log[x]['System'] == this.TodayData[y][0]['System']:
                        for z in range(0, len(this.TodayData[y][0]['Factions'])):
                            if mission_log[x]['Faction'] == this.TodayData[y][0]['Factions'][z]['Faction']:
                                this.TodayData[y][0]['Factions'][z]['MissionFailed'] += 1
                this.mission_log.delete_mission_by_index(x)
                break
        save_data()

    if entry['event'] == 'MissionAbandoned':
        this.mission_log.delete_mission_by_id(entry["MissionID"])
        save_data()

    if entry['event'] == 'ShipTargeted':
        if 'Faction' in entry and 'PilotName_Localised' in entry:
            this.LastShipTargeted = {'Faction': entry['Faction'], 'PilotName_Localised': entry['PilotName_Localised']}

    if entry['event'] == 'CommitCrime':
        # The faction logged in the CommitCrime event is the system faction, not the ship faction. So we store the
        # ship faction in LastShipTargeted from the previous ShipTargeted event.
        if entry['CrimeType'] == 'murder' and entry.get('Victim') == this.LastShipTargeted.get('PilotName_Localised'):
            for y in this.TodayData:
                if system == this.TodayData[y][0]['System']:
                    for z in range(0, len(this.TodayData[y][0]['Factions'])):
                        if this.LastShipTargeted.get('Faction') == this.TodayData[y][0]['Factions'][z]['Faction']:
                            this.TodayData[y][0]['Factions'][z]['Murdered'] += 1

    if entry['event'] == 'ApproachSettlement':
        if state['Odyssey']:
            this.LastSettlementApproached = {'timestamp': entry['timestamp'], 'name': entry['Name'], 'size': None}

    if entry['event'] == 'FactionKillBond':
        if state['Odyssey'] and this.LastSettlementApproached != {}:
            timedifference = datetime.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ') - datetime.strptime(this.LastSettlementApproached['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
            if timedifference < timedelta(minutes=5):
                # Bond issued within a short time after approaching settlement
                system_factions = this.TodayData[this.DataIndex.get()][0]['Factions']
                t = len(system_factions)
                for z in range(0, t):
                    if entry['AwardingFaction'] == system_factions[z]['Faction']:
                        # Add settlement to this faction's list, if not already present
                        if this.LastSettlementApproached['name'] not in system_factions[z]['GroundCZSettlements']:
                            system_factions[z]['GroundCZSettlements'][this.LastSettlementApproached['name']] = {'count': 0, 'enabled': CheckStates.STATE_ON}

                        # Store the previously counted size of this settlement
                        previous_size = this.LastSettlementApproached['size']

                        # Increment this settlement's overall count if this is the first bond counted
                        if this.LastSettlementApproached['size'] == None:
                            system_factions[z]['GroundCZSettlements'][this.LastSettlementApproached['name']]['count'] += 1

                        # Calculate and count CZ H/M/L - Note this isn't ideal as it counts on any kill, assuming we'll win the CZ! Also note that we re-calculate on every
                        # kill because when a kill is made my multiple players in a team, the CBs are split. We just hope that at some point we'll make a solo kill which will
                        # put this settlement into the correct CZ size category
                        if entry['Reward'] < 5000:
                            # Handle as 'Low' if this is the first CB
                            if this.LastSettlementApproached['size'] == None:
                                # Increment overall 'Low' count for this faction
                                system_factions[z]['GroundCZ']['l'] = str(int(system_factions[z]['GroundCZ'].get('l', '0')) + 1)
                                # Set faction settlement type
                                system_factions[z]['GroundCZSettlements'][this.LastSettlementApproached['name']]['type'] = 'l'
                                # Store last settlement type
                                this.LastSettlementApproached['size'] = 'l'
                        elif entry['Reward'] < 38000:
                            # Handle as 'Med' if this is either the first CB or we've counted this settlement as a 'Low' before
                            if this.LastSettlementApproached['size'] == None or this.LastSettlementApproached['size'] == 'l':
                                # Increment overall 'Med' count for this faction
                                system_factions[z]['GroundCZ']['m'] = str(int(system_factions[z]['GroundCZ'].get('m', '0')) + 1)
                                # Decrement overall previous size count if we previously counted it
                                if previous_size != None: system_factions[z]['GroundCZ'][previous_size] -= 1
                                # Set faction settlement type
                                system_factions[z]['GroundCZSettlements'][this.LastSettlementApproached['name']]['type'] = 'm'
                                # Store last settlement type
                                this.LastSettlementApproached['size'] = 'm'
                        else:
                            # Handle as 'High' if this is either the first CB or we've counted this settlement as a 'Low' or 'Med' before
                            if this.LastSettlementApproached['size'] == None or this.LastSettlementApproached['size'] == 'l' or this.LastSettlementApproached['size'] == 'm':
                                # Increment overall 'High' count for this faction
                                system_factions[z]['GroundCZ']['h'] = str(int(system_factions[z]['GroundCZ'].get('h', '0')) + 1)
                                # Decrement overall previous size count if we previously counted it
                                if previous_size != None: system_factions[z]['GroundCZ'][previous_size] -= 1
                                # Set faction settlement type
                                system_factions[z]['GroundCZSettlements'][this.LastSettlementApproached['name']]['type'] = 'h'
                                # Store last settlement type
                                this.LastSettlementApproached['size'] = 'h'
            else:
                # Too long since we last approached a settlement, we can't be sure we're fighting at that settlement, clear down
                this.LastSettlementApproached = {}


def save_data():
    """
    Save all data structures
    """
    this.mission_log.save()
    this.tick.save()
    this.activity_manager.save()
    this.prefs.save()
