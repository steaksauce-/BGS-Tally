from os import path

from bgstally.activity import Activity
from bgstally.bgstally import BGSTally
from bgstally.enums import UpdateUIPolicy

PLUGIN_VERSION = "1.10.0"

# Initialise the main plugin class
this:BGSTally = BGSTally(path.basename(path.dirname(__file__)), PLUGIN_VERSION)


def plugin_start3(plugin_dir):
    """
    Load this plugin into EDMC
    """
    this.plugin_start(plugin_dir)

    version_success = this.check_version()
    tick_success = this.check_tick(UpdateUIPolicy.NEVER)

    if tick_success == None:
        # Cannot continue if we couldn't fetch a tick
        raise Exception("BGS-Tally couldn't continue because the current tick could not be fetched")

    return this.plugin_name


def plugin_stop():
    """
    EDMC is closing
    """
    this.plugin_stop()


def plugin_app(parent):
    """
    Return a TK Frame for adding to the EDMC main window
    """
    return this.ui.get_plugin_frame(parent, this.git_version)


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
    dirty: bool = False

    if entry['event'] in ['Location', 'FSDJump', 'CarrierJump']:
        if this.check_tick(UpdateUIPolicy.IMMEDIATE):
            # New activity will be generated with a new tick
            activity = this.activity_manager.get_current_activity()

        activity.system_entered(entry, this.state)
        dirty = True

    match entry['event']:
        case 'Docked':
            this.state.station_faction = entry['StationFaction']['Name']
            this.state.station_type = entry['StationType']
            dirty = True

        case 'Location' | 'StartUp' if entry['Docked'] == True:
            this.state.station_type = entry['StationType']
            dirty = True

        case 'SellExplorationData' | 'MultiSellExplorationData':
            activity.exploration_data_sold(entry, this.state)
            dirty = True

        case 'SellOrganicData':
            activity.organic_data_sold(entry, this.state)
            dirty = True

        case 'RedeemVoucher' if entry['Type'] == 'bounty':
            activity.bv_redeemed(entry, this.state)
            dirty = True

        case 'RedeemVoucher' if entry['Type'] == 'CombatBond':
            activity.cb_redeemed(entry, this.state)
            dirty = True

        case 'MarketBuy':
            activity.trade_purchased(entry, this.state)
            dirty = True

        case 'MarketSell':
            activity.trade_sold(entry, this.state)
            dirty = True

        case 'MissionAccepted':
            this.mission_log.add_mission(entry['Name'], entry['Faction'], entry['MissionID'], entry['Expiry'], system)
            dirty = True

        case 'MissionAbandoned':
            this.mission_log.delete_mission_by_id(entry['MissionID'])
            dirty = True

        case 'MissionFailed':
            activity.mission_failed(entry, this.mission_log)
            dirty = True

        case 'MissionCompleted':
            activity.mission_completed(entry, this.mission_log)
            dirty = True

        case 'ShipTargeted':
            activity.ship_targeted(entry, this.state)
            dirty = True

        case 'CommitCrime':
            activity.crime_committed(entry, this.state)
            dirty = True

        case 'ApproachSettlement' if state['Odyssey']:
            activity.settlement_approached(entry, this.state)
            dirty = True

        case 'FactionKillBond' if state['Odyssey']:
            activity.cb_received(entry, this.state)
            dirty = True

    if dirty: this.save_data()
