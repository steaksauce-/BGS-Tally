import sys
from os import path
from xmlrpc.client import boolean

import plug
import requests

from bgstally.activity import Activity
from bgstally.activitymanager import ActivityManager
from bgstally.debug import Debug
from bgstally.discord import Discord
from bgstally.missionlog import MissionLog
from bgstally.state import State
from bgstally.fleetcarrier import FleetCarrier
#from bgstally.overlay import Overlay
from bgstally.tick import Tick
from bgstally.ui import UI

this = sys.modules[__name__]  # For holding module globals

this.plugin_name = path.basename(path.dirname(__file__))
this.VersionNo = "1.10.0"
this.GitVersion = "0.0.0"


def plugin_start3(plugin_dir):
    """
    Load this plugin into EDMC
    """
    # Classes
    this.debug: Debug = Debug(this.plugin_name)
    this.state: State = State()
    this.mission_log: MissionLog = MissionLog(plugin_dir)
    this.discord: Discord = Discord(this.state)
    #this.overlay = Overlay()
    this.tick: Tick = Tick(True)
    this.activity_manager: ActivityManager = ActivityManager(plugin_dir, this.mission_log, this.tick)
    this.fleet_carrier = FleetCarrier()
    this.ui: UI = UI(plugin_dir, this.state, this.activity_manager, this.tick, this.discord, this.fleet_carrier, this.VersionNo)

    version_success = check_version()
    tick_success = this.tick.fetch_tick()

    if tick_success == None:
        # Cannot continue if we couldn't fetch a tick
        raise Exception("BGS-Tally couldn't continue because the current tick could not be fetched")
    elif tick_success == True:
        this.ui.new_tick(False, False)

    #this.overlay.display_message("tickwarn", f"Tick: {this.tick.get_formatted()}")
    #this.discord.post_to_fcjump_discord(this.fleet_carrier.get_formatted_materials())

    return this.plugin_name


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


def journal_entry(cmdr, is_beta, system, station, entry, state):
    """
    Parse an incoming journal entry and store the data we need
    """
    if this.state.Status.get() != "Active": return

    activity: Activity = this.activity_manager.get_current_activity()
    dirty: boolean = False

    if entry['event'] in ['Location', 'FSDJump', 'CarrierJump']:
        # Check for a new tick
        if this.tick.fetch_tick():
            this.ui.new_tick(False, True)
            activity = this.activity_manager.get_current_activity() # New activity will be generated with a new tick

        activity.system_entered(entry, this.state)
        dirty = True

    if entry['event'] == 'Docked':
        this.state.station_faction = entry['StationFaction']['Name']
        this.state.station_type = entry['StationType']
        dirty = True

    if (entry['event'] == 'Location' or entry['event'] == 'StartUp') and entry['Docked'] == True:
        this.state.station_type = entry['StationType']
        dirty = True

    if entry['event'] == 'SellExplorationData' or entry['event'] == 'MultiSellExplorationData':
        activity.exploration_data_sold(entry, this.state)
        dirty = True

    if entry['event'] == 'SellOrganicData':
        activity.organic_data_sold(entry, this.state)
        dirty = True

    if entry['event'] == 'RedeemVoucher' and entry['Type'] == 'bounty':
        activity.bv_redeemed(entry, this.state)
        dirty = True

    if entry['event'] == 'RedeemVoucher' and entry['Type'] == 'CombatBond':
        activity.cb_redeemed(entry, this.state)
        dirty = True

    if entry['event'] == 'MarketBuy':
        activity.trade_purchased(entry, this.state)
        dirty = True

    if entry['event'] == 'MarketSell':
        activity.trade_sold(entry, this.state)
        dirty = True

    if entry['event'] == 'MissionAccepted':
        this.mission_log.add_mission(entry['Name'], entry['Faction'], entry['MissionID'], entry['Expiry'], system)
        dirty = True

    if entry['event'] == 'MissionAbandoned':
        this.mission_log.delete_mission_by_id(entry['MissionID'])
        dirty = True

    if entry['event'] == 'MissionFailed':
        activity.mission_failed(entry, this.mission_log)
        dirty = True

    if entry['event'] == 'MissionCompleted':
        activity.mission_completed(entry, this.mission_log)
        dirty = True

    if entry['event'] == 'ShipTargeted':
        activity.ship_targeted(entry, this.state)
        dirty = True

    if entry['event'] == 'CommitCrime':
        activity.crime_committed(entry, system, this.state)
        dirty = True

    if entry['event'] == 'ApproachSettlement' and state['Odyssey']:
        activity.settlement_approached(entry, this.state)
        dirty = True

    if entry['event'] == 'FactionKillBond' and state['Odyssey']:
        activity.cb_received(entry, this.state)
        dirty = True

    if dirty: save_data()


def check_version():
    """
    Check for a new plugin version
    """
    try:
        response = requests.get("https://api.github.com/repos/aussig/BGS-Tally/releases/latest", timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        this.debug.logger.warning(f"Unable to fetch latest plugin version", exc_info=e)
        plug.show_error(f"BGS-Tally: Unable to fetch latest plugin version")
        return None
    else:
        latest = response.json()
        this.GitVersion = latest['tag_name']

    return True


def save_data():
    """
    Save all data structures
    """
    this.mission_log.save()
    this.tick.save()
    this.activity_manager.save()
    this.state.save()
