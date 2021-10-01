import json
import logging
import os.path
import sys
import tkinter as tk
import webbrowser
from datetime import datetime
from enum import Enum
from functools import partial
from os import path
from tkinter import ttk

import myNotebook as nb
import requests
from config import appname, config
from theme import theme

this = sys.modules[__name__]  # For holding module globals
this.VersionNo = "1.5.0"
this.FactionNames = []
this.TodayData = {}
this.YesterdayData = {}
this.DataIndex = 0
this.TickTime = ""
this.State = tk.IntVar()
this.MissionLog = []

# Conflict states, for determining whether we display the CZ UI and count conflict missions for factions in these states
this.ConflictStates = [
    'War', 'CivilWar'
]

# Missions that we count as +1 INF in Elections even if the Journal reports no +INF
this.MissionListElection = [
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
this.MissionListConflict = [
    'Mission_Assassinate_Legal_CivilWar_name', 'Mission_Assassinate_Legal_War_name',
    'Mission_Massacre_Conflict_CivilWar_name', 'Mission_Massacre_Conflict_War_name',
    'Mission_OnFoot_Onslaught_Offline_MB_name'
]

# Plugin Preferences on settings tab. These are all initialised to Variables in plugin_start3
this.Status = None
this.AbbreviateFactionNames = None
this.DiscordWebhook = None
this.DiscordUsername = None


# This could also be returned from plugin_start3()
plugin_name = os.path.basename(os.path.dirname(__file__))

# A Logger is used per 'found' plugin to make it easy to include the plugin's
# folder name in the logging output format.
# NB: plugin_name here *must* be the plugin's folder name as per the preceding
#     code, else the logger won't be properly set up.
logger = logging.getLogger(f'{appname}.{plugin_name}')

# If the Logger has handlers then it was already set up by the core code, else
# it needs setting up here.
if not logger.hasHandlers():
    level = logging.INFO  # So logger.info(...) is equivalent to print()

    logger.setLevel(level)
    logger_channel = logging.StreamHandler()
    logger_formatter = logging.Formatter(f'%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%(funcName)s: %(message)s')
    logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S'
    logger_formatter.default_msec_format = '%s.%03d'
    logger_channel.setFormatter(logger_formatter)
    logger.addHandler(logger_channel)


class CZs(Enum):
    SPACE_HIGH = 0
    SPACE_MED = 1
    SPACE_LOW = 2
    GROUND_HIGH = 3
    GROUND_MED = 4
    GROUND_LOW = 5

class Ticks(Enum):
    TICK_CURRENT = 0
    TICK_PREVIOUS = 1

# Subclassing from str as well as Enum means json.load and json.dump work seamlessly
class CheckStates(str, Enum):
    STATE_OFF = 'No'
    STATE_ON = 'Yes'
    STATE_PARTIAL = 'Partial'
    STATE_PENDING = 'Pending'


def plugin_prefs(parent, cmdr, is_beta):
    """
    Return a TK Frame for adding to the EDMC settings dialog.
    """
    frame = nb.Frame(parent)
    # Make the second column fill available space
    frame.columnconfigure(1, weight=1)

    nb.Label(frame, text="BGS Tally (modified by Aussi) v" + this.VersionNo).grid(columnspan=2, padx=10, sticky=tk.W)
    ttk.Separator(frame, orient=tk.HORIZONTAL).grid(columnspan=2, padx=10, pady=2, sticky=tk.EW)
    nb.Checkbutton(frame, text="BGS Tally Active", variable=this.Status, onvalue="Active", offvalue="Paused").grid(column=1, padx=10, sticky=tk.W)
    nb.Checkbutton(frame, text="Abbreviate Faction Names", variable=this.AbbreviateFactionNames, onvalue="Yes", offvalue="No").grid(column=1, padx=10, sticky=tk.W)
    nb.Label(frame, text="Discord Webhook URL").grid(column=0, padx=10, sticky=tk.W, row=5)
    nb.Entry(frame, textvariable=this.DiscordWebhook).grid(column=1, padx=10, pady=2, sticky=tk.EW, row=5)
    nb.Label(frame, text="Discord Post as User").grid(column=0, padx=10, sticky=tk.W, row=6)
    nb.Entry(frame, textvariable=this.DiscordUsername).grid(column=1, padx=10, pady=2, sticky=tk.W, row=6)

    return frame


def prefs_changed(cmdr, is_beta):
    """
    Save settings.
    """
    this.StatusLabel["text"] = this.Status.get()


def plugin_start3(plugin_dir):
    """
    Load this plugin into EDMC
    """
    this.Dir = plugin_dir
    file = os.path.join(this.Dir, "Today Data.txt")
    if path.exists(file):
        with open(file) as json_file:
            this.TodayData = json.load(json_file)
            z = len(this.TodayData)
            for i in range(1, z + 1):
                x = str(i)
                this.TodayData[i] = this.TodayData[x]
                del this.TodayData[x]
    file = os.path.join(this.Dir, "Yesterday Data.txt")
    if path.exists(file):
        with open(file) as json_file:
            this.YesterdayData = json.load(json_file)
            z = len(this.YesterdayData)
            for i in range(1, z + 1):
                x = str(i)
                this.YesterdayData[i] = this.YesterdayData[x]
                del this.YesterdayData[x]
    file = os.path.join(this.Dir, "MissionLog.txt")
    if path.exists(file):
        with open(file) as json_file:
            this.MissionLog = json.load(json_file)
    this.LastTick = tk.StringVar(value=config.get_str("XLastTick"))
    this.TickTime = tk.StringVar(value=config.get_str("XTickTime"))
    this.Status = tk.StringVar(value=config.get_str("XStatus"))
    this.AbbreviateFactionNames = tk.StringVar(value=config.get_str("XAbbreviate"))
    this.DiscordWebhook = tk.StringVar(value=config.get_str("XDiscordWebhook"))
    this.DiscordUsername = tk.StringVar(value=config.get_str("XDiscordUsername"))
    this.DiscordCurrentMessageID = tk.StringVar(value=config.get_str("XDiscordCurrentMessageID"))
    this.DiscordPreviousMessageID = tk.StringVar(value=config.get_str("XDiscordPreviousMessageID"))
    this.DataIndex = tk.IntVar(value=config.get_int("xIndex"))
    this.StationFaction = tk.StringVar(value=config.get_str("XStation"))
    response = requests.get('https://api.github.com/repos/aussig/BGS-Tally/releases/latest')  # check latest version
    latest = response.json()
    this.GitVersion = latest['tag_name']
    check_tick()

    return "BGS Tally"


def plugin_stop():
    """
    EDMC is closing
    """
    save_data()


def plugin_app(parent):
    """
    Create a frame for the EDMC main window
    """
    this.frame = tk.Frame(parent)
    Title = tk.Label(this.frame, text="BGS Tally (modified by Aussi) v" + this.VersionNo)
    Title.grid(row=0, column=0, sticky=tk.W)
    if version_tuple(this.GitVersion) > version_tuple(this.VersionNo):
        title2 = tk.Label(this.frame, text="New version available", fg="blue", cursor="hand2")
        title2.grid(row=0, column=1, sticky=tk.W, )
        title2.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/aussig/BGS-Tally/releases"))
    tk.Button(this.frame, text='Latest BGS Tally', command=display_todaydata).grid(row=1, column=0, padx=3)
    tk.Button(this.frame, text='Previous BGS Tally', command=display_yesterdaydata).grid(row=1, column=1, padx=3)
    tk.Label(this.frame, text="BGS Tally Plugin Status:").grid(row=2, column=0, sticky=tk.W)
    tk.Label(this.frame, text="Last BGS Tick:").grid(row=3, column=0, sticky=tk.W)
    this.StatusLabel = tk.Label(this.frame, text=this.Status.get()).grid(row=2, column=1, sticky=tk.W)
    this.TimeLabel = tk.Label(this.frame, text=tick_format(this.TickTime)).grid(row=3, column=1, sticky=tk.W)
    return this.frame


def check_tick():
    """
    Tick check and counter reset
    """
    response = requests.get('https://elitebgs.app/api/ebgs/v5/ticks')  # get current tick and reset if changed
    tick = response.json()
    this.CurrentTick = tick[0]['_id']
    this.TickTime = tick[0]['time']
    if this.LastTick.get() != this.CurrentTick:
        this.LastTick.set(this.CurrentTick)
        this.YesterdayData = this.TodayData
        this.TodayData = {}
        this.DiscordPreviousMessageID.set(this.DiscordCurrentMessageID.get())
        this.DiscordCurrentMessageID.set('')
        return True

    return False


def journal_entry(cmdr, is_beta, system, station, entry, state):
    """
    Parse an incoming journal entry and store the data we need
    """
    EventList = ['Location', 'FSDJump', 'CarrierJump']
    if this.Status.get() != "Active":
        return
    if entry['event'] in EventList:  # get factions and populate today data
        this.FactionNames = []
        this.FactionStates = []
        z = 0
        try:
            test = entry['Factions']
        except KeyError:
            return
        for i in entry['Factions']:
            if i['Name'] != "Pilots' Federation Local Branch":
                this.FactionNames.append(i['Name'])
                this.FactionStates.append({'Faction': i['Name'], 'State': i['FactionState']})
                z += 1
        x = len(this.TodayData)
        if (x >= 1):
            for y in range(1, x + 1):
                if entry['StarSystem'] == this.TodayData[y][0]['System']:
                    this.DataIndex.set(y)
                    return
            this.TodayData[x + 1] = [
                {'System': entry['StarSystem'], 'SystemAddress': entry['SystemAddress'], 'Factions': []}]
            this.DataIndex.set(x + 1)
            z = len(this.FactionNames)
            for i in range(0, z):
                this.TodayData[x + 1][0]['Factions'].append(
                    {'Faction': this.FactionNames[i], 'FactionState': this.FactionStates[i]['State'],
                     'MissionPoints': 0,
                     'TradeProfit': 0, 'Bounties': 0, 'CartData': 0,
                     'CombatBonds': 0, 'MissionFailed': 0, 'Murdered': 0,
                     'SpaceCZ': {},
                     'GroundCZ': {}})
        else:
            this.TodayData = {
                1: [{'System': entry['StarSystem'], 'SystemAddress': entry['SystemAddress'], 'Factions': []}]}
            z = len(this.FactionNames)
            this.DataIndex.set(1)
            for i in range(0, z):
                this.TodayData[1][0]['Factions'].append(
                    {'Faction': this.FactionNames[i], 'FactionState': this.FactionStates[i]['State'],
                     'MissionPoints': 0,
                     'TradeProfit': 0, 'Bounties': 0, 'CartData': 0,
                     'CombatBonds': 0, 'MissionFailed': 0, 'Murdered': 0,
                     'SpaceCZ': {},
                     'GroundCZ': {}})

    if entry['event'] == 'Docked':  # enter system and faction named
        this.StationFaction.set(entry['StationFaction']['Name'])  # set controlling faction name
        # Check for a new tick
        if check_tick():
            this.TimeLabel = tk.Label(this.frame, text=tick_format(this.TickTime)).grid(row=3, column=1, sticky=tk.W)
            theme.update(this.frame)

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
                                    this.TodayData[y][0]['Factions'][z]['MissionPoints'] += inf
                                else:
                                    this.TodayData[y][0]['Factions'][z]['MissionPoints'] -= inf
            else:
                for p in range(len(this.MissionLog)):
                    if this.MissionLog[p]["MissionID"] == entry["MissionID"]:
                        for y in this.TodayData:
                            if this.MissionLog[p]['System'] == this.TodayData[y][0]['System']:
                                for z in range(0, len(this.TodayData[y][0]['Factions'])):
                                    if this.TodayData[y][0]['Factions'][z]['Faction'] == fe3:
                                        if (this.TodayData[y][0]['Factions'][z]['FactionState'] == 'Election' and entry['Name'] in this.MissionListElection) \
                                        or (this.TodayData[y][0]['Factions'][z]['FactionState'] in this.ConflictStates and entry['Name'] in this.MissionListConflict):
                                            this.TodayData[y][0]['Factions'][z]['MissionPoints'] += 1
        for count in range(len(this.MissionLog)):
            if this.MissionLog[count]["MissionID"] == entry["MissionID"]:
                this.MissionLog.pop(count)
                break
        save_data()

    if entry['event'] == 'SellExplorationData' or entry['event'] == "MultiSellExplorationData":  # get carto data value
        t = len(this.TodayData[this.DataIndex.get()][0]['Factions'])
        for z in range(0, t):
            if this.StationFaction.get() == this.TodayData[this.DataIndex.get()][0]['Factions'][z]['Faction']:
                this.TodayData[this.DataIndex.get()][0]['Factions'][z]['CartData'] += entry['TotalEarnings']
        save_data()

    if entry['event'] == 'RedeemVoucher' and entry['Type'] == 'bounty':  # bounties collected
        t = len(this.TodayData[this.DataIndex.get()][0]['Factions'])
        for z in entry['Factions']:
            for x in range(0, t):
                if z['Faction'] == this.TodayData[this.DataIndex.get()][0]['Factions'][x]['Faction']:
                    this.TodayData[this.DataIndex.get()][0]['Factions'][x]['Bounties'] += z['Amount']
        save_data()

    if entry['event'] == 'RedeemVoucher' and entry['Type'] == 'CombatBond':  # combat bonds collected
        t = len(this.TodayData[this.DataIndex.get()][0]['Factions'])
        for x in range(0, t):
            if entry['Faction'] == this.TodayData[this.DataIndex.get()][0]['Factions'][x]['Faction']:
                this.TodayData[this.DataIndex.get()][0]['Factions'][x]['CombatBonds'] += entry['Amount']
        save_data()

    if entry['event'] == 'MarketSell':  # Trade Profit
        t = len(this.TodayData[this.DataIndex.get()][0]['Factions'])
        for z in range(0, t):
            if this.StationFaction.get() == this.TodayData[this.DataIndex.get()][0]['Factions'][z]['Faction']:
                cost = entry['Count'] * entry['AvgPricePaid']
                profit = entry['TotalSale'] - cost
                this.TodayData[this.DataIndex.get()][0]['Factions'][z]['TradeProfit'] += profit
        save_data()

    if entry['event'] == 'MissionAccepted':  # mission accpeted
        this.MissionLog.append({"Name": entry["Name"], "Faction": entry["Faction"], "MissionID": entry["MissionID"],
                                "System": system})
        save_data()

    if entry['event'] == 'MissionFailed':  # mission failed
        for x in range(len(this.MissionLog)):
            if this.MissionLog[x]["MissionID"] == entry["MissionID"]:
                for y in this.TodayData:
                    if this.MissionLog[x]['System'] == this.TodayData[y][0]['System']:
                        for z in range(0, len(this.TodayData[y][0]['Factions'])):
                            if this.MissionLog[x]['Faction'] == this.TodayData[y][0]['Factions'][z]['Faction']:
                                this.TodayData[y][0]['Factions'][z]['MissionFailed'] += 1
                this.MissionLog.pop(x)
                break
        save_data()

    if entry['event'] == 'MissionAbandoned':
        for x in range(len(this.MissionLog)):
            if this.MissionLog[x]["MissionID"] == entry["MissionID"]:
                this.MissionLog.pop(x)
        save_data()

    if entry['event'] == 'CommitCrime':
        if entry['CrimeType'] == 'murder':
            for y in this.TodayData:
                if system == this.TodayData[y][0]['System']:
                    for z in range(0, len(this.TodayData[y][0]['Factions'])):
                        if entry['Faction'] == this.TodayData[y][0]['Factions'][z]['Faction']:
                            this.TodayData[y][0]['Factions'][z]['Murdered'] += 1


def version_tuple(version):
    """
    Parse the plugin version number into a tuple
    """
    try:
        ret = tuple(map(int, version.split(".")))
    except:
        ret = (0,)
    return ret


def human_format(num):
    """
    Format a BGS value into shortened human-readable text
    """
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def update_faction_data(faction_data):
    """
    Update faction data structure for elements not present in previous versions of plugin
    """
    # From < v1.2.0 to 1.2.0
    if not 'SpaceCZ' in faction_data: faction_data['SpaceCZ'] = {}
    if not 'GroundCZ' in faction_data: faction_data['GroundCZ'] = {}
    # From < v1.3.0 to 1.3.0
    if not 'Enabled' in faction_data: faction_data['Enabled'] = CheckStates.STATE_ON


def display_data(title, data, tick_mode):
    """
    Display the data window, using either latest or previous data
    """
    heading_font = ("Helvetica", 11, 'bold')
    Form = tk.Toplevel(this.frame)
    Form.title("BGS Tally v" + this.VersionNo + " - " + title)
    Form.geometry("1000x700")

    ContainerFrame = ttk.Frame(Form)
    ContainerFrame.pack(fill=tk.BOTH, expand=1)
    TabParent = ttk.Notebook(ContainerFrame)
    TabParent.pack(fill=tk.BOTH, expand=1, side=tk.TOP, padx=5, pady=5)
    ttk.Label(ContainerFrame, text="Discord Report:", font=heading_font, anchor=tk.W).pack(fill=tk.BOTH, padx=5, pady=5)
    Discord = tk.Text(ContainerFrame, wrap = tk.WORD, height=17, font = ("Helvetica", 9))
    Discord.pack(fill=tk.X, padx=5, pady=5)

    for i in data:
        tab = ttk.Frame(TabParent)
        # Make the second column (faction name) fill available space
        tab.columnconfigure(1, weight=1)

        FactionEnableCheckbuttons = []

        TabParent.add(tab, text=data[i][0]['System'])
        ttk.Label(tab, text="Include", font=heading_font).grid(row=0, column=0, padx=2, pady=2)
        EnableAllCheckbutton = ttk.Checkbutton(tab)
        EnableAllCheckbutton.grid(row=1, column=0, padx=2, pady=2)
        EnableAllCheckbutton.configure(command=partial(enable_all_factions_change, EnableAllCheckbutton, FactionEnableCheckbuttons, Discord, data, i))
        EnableAllCheckbutton.state(['!alternate'])
        ttk.Label(tab, text="Faction", font=heading_font).grid(row=0, column=1, padx=2, pady=2)
        ttk.Label(tab, text="State", font=heading_font).grid(row=0, column=2, padx=2, pady=2)
        ttk.Label(tab, text="INF", font=heading_font).grid(row=0, column=3, padx=2, pady=2)
        ttk.Label(tab, text="Trade", font=heading_font).grid(row=0, column=4, padx=2, pady=2)
        ttk.Label(tab, text="BVs", font=heading_font).grid(row=0, column=5, padx=2, pady=2)
        ttk.Label(tab, text="Expl", font=heading_font).grid(row=0, column=6, padx=2, pady=2)
        ttk.Label(tab, text="CBs", font=heading_font).grid(row=0, column=7, padx=2, pady=2)
        ttk.Label(tab, text="Fails", font=heading_font).grid(row=0, column=8, padx=2, pady=2)
        ttk.Label(tab, text="Murders", font=heading_font).grid(row=0, column=9, padx=2, pady=2)
        ttk.Label(tab, text="Space CZs", font=heading_font, width=18, anchor=tk.CENTER).grid(row=0, column=10, columnspan=3, padx=2)
        ttk.Label(tab, text="L", font=heading_font).grid(row=1, column=10, padx=2, pady=2)
        ttk.Label(tab, text="M", font=heading_font).grid(row=1, column=11, padx=2, pady=2)
        ttk.Label(tab, text="H", font=heading_font).grid(row=1, column=12, padx=2, pady=2)
        ttk.Label(tab, text="On-foot CZs", font=heading_font, width=18, anchor=tk.CENTER).grid(row=0, column=13, columnspan=3, padx=2)
        ttk.Label(tab, text="L", font=heading_font).grid(row=1, column=13, padx=2, pady=2)
        ttk.Label(tab, text="M", font=heading_font).grid(row=1, column=14, padx=2, pady=2)
        ttk.Label(tab, text="H", font=heading_font).grid(row=1, column=15, padx=2, pady=2)
        ttk.Separator(tab, orient=tk.HORIZONTAL).grid(columnspan=16, padx=2, pady=5, sticky=tk.EW)

        header_rows = 3
        z = len(data[i][0]['Factions'])

        for x in range(0, z):
            update_faction_data(data[i][0]['Factions'][x])

            EnableCheckbutton = ttk.Checkbutton(tab)
            EnableCheckbutton.grid(row=x + header_rows, column=0, padx=2, pady=2)
            EnableCheckbutton.configure(command=partial(enable_faction_change, EnableAllCheckbutton, FactionEnableCheckbuttons, Discord, data, i, x))
            EnableCheckbutton.state(['selected', '!alternate'] if data[i][0]['Factions'][x]['Enabled'] == CheckStates.STATE_ON else ['!selected', '!alternate'])
            FactionEnableCheckbuttons.append(EnableCheckbutton)
            FactionName = ttk.Label(tab, text=data[i][0]['Factions'][x]['Faction'])
            FactionName.grid(row=x + header_rows, column=1, sticky=tk.W, padx=2, pady=2)
            FactionName.bind("<Button-1>", partial(faction_name_clicked, EnableCheckbutton, EnableAllCheckbutton, FactionEnableCheckbuttons, Discord, data, i, x))
            ttk.Label(tab, text=data[i][0]['Factions'][x]['FactionState']).grid(row=x + header_rows, column=2)
            MissionPointsVar = tk.IntVar(value=data[i][0]['Factions'][x]['MissionPoints'])
            ttk.Spinbox(tab, from_=-999, to=999, width=3, textvariable=MissionPointsVar).grid(row=x + header_rows, column=3, padx=2, pady=2)
            ttk.Label(tab, text=human_format(data[i][0]['Factions'][x]['TradeProfit'])).grid(row=x + header_rows, column=4)
            ttk.Label(tab, text=human_format(data[i][0]['Factions'][x]['Bounties'])).grid(row=x + header_rows, column=5)
            ttk.Label(tab, text=human_format(data[i][0]['Factions'][x]['CartData'])).grid(row=x + header_rows, column=6)
            ttk.Label(tab, text=human_format(data[i][0]['Factions'][x]['CombatBonds'])).grid(row=x + header_rows, column=7)
            ttk.Label(tab, text=data[i][0]['Factions'][x]['MissionFailed']).grid(row=x + header_rows, column=8)
            ttk.Label(tab, text=data[i][0]['Factions'][x]['Murdered']).grid(row=x + header_rows, column=9)
            MissionPointsVar.trace('w', partial(mission_points_change, MissionPointsVar, Discord, data, i, x))

            if (data[i][0]['Factions'][x]['FactionState'] in this.ConflictStates):
                CZSpaceLVar = tk.StringVar(value=data[i][0]['Factions'][x]['SpaceCZ'].get('l', '0'))
                ttk.Spinbox(tab, from_=0, to=999, width=3, textvariable=CZSpaceLVar).grid(row=x + header_rows, column=10, padx=2, pady=2)
                CZSpaceMVar = tk.StringVar(value=data[i][0]['Factions'][x]['SpaceCZ'].get('m', '0'))
                ttk.Spinbox(tab, from_=0, to=999, width=3, textvariable=CZSpaceMVar).grid(row=x + header_rows, column=11, padx=2, pady=2)
                CZSpaceHVar = tk.StringVar(value=data[i][0]['Factions'][x]['SpaceCZ'].get('h', '0'))
                ttk.Spinbox(tab, from_=0, to=999, width=3, textvariable=CZSpaceHVar).grid(row=x + header_rows, column=12, padx=2, pady=2)
                CZGroundLVar = tk.StringVar(value=data[i][0]['Factions'][x]['GroundCZ'].get('l', '0'))
                ttk.Spinbox(tab, from_=0, to=999, width=3, textvariable=CZGroundLVar).grid(row=x + header_rows, column=13, padx=2, pady=2)
                CZGroundMVar = tk.StringVar(value=data[i][0]['Factions'][x]['GroundCZ'].get('m', '0'))
                ttk.Spinbox(tab, from_=0, to=999, width=3, textvariable=CZGroundMVar).grid(row=x + header_rows, column=14, padx=2, pady=2)
                CZGroundHVar = tk.StringVar(value=data[i][0]['Factions'][x]['GroundCZ'].get('h', '0'))
                ttk.Spinbox(tab, from_=0, to=999, width=3, textvariable=CZGroundHVar).grid(row=x + header_rows, column=15, padx=2, pady=2)
                # Watch for changes on all SpinBox Variables. This approach catches any change, including manual editing, while using 'command' callbacks only catches clicks
                CZSpaceLVar.trace('w', partial(cz_change, CZSpaceLVar, Discord, CZs.SPACE_LOW, data, i, x))
                CZSpaceMVar.trace('w', partial(cz_change, CZSpaceMVar, Discord, CZs.SPACE_MED, data, i, x))
                CZSpaceHVar.trace('w', partial(cz_change, CZSpaceHVar, Discord, CZs.SPACE_HIGH, data, i, x))
                CZGroundLVar.trace('w', partial(cz_change, CZGroundLVar, Discord, CZs.GROUND_LOW, data, i, x))
                CZGroundMVar.trace('w', partial(cz_change, CZGroundMVar, Discord, CZs.GROUND_MED, data, i, x))
                CZGroundHVar.trace('w', partial(cz_change, CZGroundHVar, Discord, CZs.GROUND_HIGH, data, i, x))

        update_enable_all_factions_checkbutton(EnableAllCheckbutton, FactionEnableCheckbuttons)

    Discord.insert(tk.INSERT, generate_discord_text(data))
    # Select all text and focus the field
    Discord.tag_add('sel', '1.0', 'end')
    Discord.focus()

    ttk.Button(ContainerFrame, text="Copy to Clipboard", command=partial(copy_to_clipboard, ContainerFrame, Discord)).pack(side=tk.LEFT, padx=5, pady=5)
    if is_webhook_valid(): ttk.Button(ContainerFrame, text="Post to Discord", command=partial(post_to_discord, ContainerFrame, Discord, tick_mode)).pack(side=tk.RIGHT, padx=5, pady=5)

    theme.update(ContainerFrame)

    # Ignore all scroll wheel events on spinboxes, to avoid accidental inputs
    Form.bind_class('TSpinbox', '<MouseWheel>', lambda event : "break")


def cz_change(CZVar, Discord, cz_type, data, system_index, faction_index, *args):
    """
    Callback (set as a variable trace) for when a CZ Variable is changed
    """
    if cz_type == CZs.SPACE_LOW:
        data[system_index][0]['Factions'][faction_index]['SpaceCZ']['l'] = CZVar.get()
    elif cz_type == CZs.SPACE_MED:
        data[system_index][0]['Factions'][faction_index]['SpaceCZ']['m'] = CZVar.get()
    elif cz_type == CZs.SPACE_HIGH:
        data[system_index][0]['Factions'][faction_index]['SpaceCZ']['h'] = CZVar.get()
    elif cz_type == CZs.GROUND_LOW:
        data[system_index][0]['Factions'][faction_index]['GroundCZ']['l'] = CZVar.get()
    elif cz_type == CZs.GROUND_MED:
        data[system_index][0]['Factions'][faction_index]['GroundCZ']['m'] = CZVar.get()
    elif cz_type == CZs.GROUND_HIGH:
        data[system_index][0]['Factions'][faction_index]['GroundCZ']['h'] = CZVar.get()

    Discord.delete('1.0', 'end-1c')
    Discord.insert(tk.INSERT, generate_discord_text(data))


def enable_faction_change(EnableAllCheckbutton, FactionEnableCheckbuttons, Discord, data, system_index, faction_index, *args):
    """
    Callback  for when a Faction Enable Checkbutton is changed
    """
    data[system_index][0]['Factions'][faction_index]['Enabled'] = CheckStates.STATE_ON if FactionEnableCheckbuttons[faction_index].instate(['selected']) else CheckStates.STATE_OFF
    update_enable_all_factions_checkbutton(EnableAllCheckbutton, FactionEnableCheckbuttons)

    Discord.delete('1.0', 'end-1c')
    Discord.insert(tk.INSERT, generate_discord_text(data))


def enable_all_factions_change(EnableAllCheckbutton, FactionEnableCheckbuttons, Discord, data, system_index, *args):
    """
    Callback for when the Enable All Factions Checkbutton is changed
    """
    z = len(FactionEnableCheckbuttons)
    for x in range(0, z):
        if EnableAllCheckbutton.instate(['selected']):
            FactionEnableCheckbuttons[x].state(['selected'])
            data[system_index][0]['Factions'][x]['Enabled'] = CheckStates.STATE_ON
        else:
            FactionEnableCheckbuttons[x].state(['!selected'])
            data[system_index][0]['Factions'][x]['Enabled'] = CheckStates.STATE_OFF

    Discord.delete('1.0', 'end-1c')
    Discord.insert(tk.INSERT, generate_discord_text(data))


def update_enable_all_factions_checkbutton(EnableAllCheckbutton, FactionEnableCheckbuttons):
    """
    Update the 'Enable all factions' checkbox to the correct state based on which individual factions are enabled
    """
    any_on = False
    any_off = False
    z = len(FactionEnableCheckbuttons)
    for x in range(0, z):
        if FactionEnableCheckbuttons[x].instate(['selected']): any_on = True
        if FactionEnableCheckbuttons[x].instate(['!selected']): any_off = True

    if any_on == True:
        if any_off == True:
            EnableAllCheckbutton.state(['alternate', '!selected'])
        else:
            EnableAllCheckbutton.state(['!alternate', 'selected'])
    else:
        EnableAllCheckbutton.state(['!alternate', '!selected'])


def faction_name_clicked(EnableCheckbutton, EnableAllCheckbutton, FactionEnableCheckbuttons, Discord, data, system_index, faction_index, *args):
    """
    Callback when a faction name is clicked. Toggle enabled state. The EnableVar is watched, so that will
    automatically trigger enable_faction_change() to update data and Discord text
    """
    if EnableCheckbutton.instate(['selected']): EnableCheckbutton.state(['!selected'])
    else: EnableCheckbutton.state(['selected'])
    enable_faction_change(EnableAllCheckbutton, FactionEnableCheckbuttons, Discord, data, system_index, faction_index, *args)


def mission_points_change(MissionPointsVar, Discord, data, system_index, faction_index, *args):
    """
    Callback (set as a variable trace) for when a mission points Variable is changed
    """
    data[system_index][0]['Factions'][faction_index]['MissionPoints'] = MissionPointsVar.get()

    Discord.delete('1.0', 'end-1c')
    Discord.insert(tk.INSERT, generate_discord_text(data))


def generate_discord_text(data):
    """
    Generate the Discord-formatted version of the tally data
    """
    discord_text = ""

    for i in data:
        system_discord_text = ""
        z = len(data[i][0]['Factions'])

        for x in range(0, z):
            if data[i][0]['Factions'][x]['Enabled'] != CheckStates.STATE_ON: continue

            faction_discord_text = ""

            if data[i][0]['Factions'][x]['FactionState'] == 'Election':
                faction_discord_text += f".ElectionINF {data[i][0]['Factions'][x]['MissionPoints']}; " if data[i][0]['Factions'][x]['MissionPoints'] > 0 else ""
            elif data[i][0]['Factions'][x]['FactionState'] in this.ConflictStates:
                faction_discord_text += f".WarINF {data[i][0]['Factions'][x]['MissionPoints']}; " if data[i][0]['Factions'][x]['MissionPoints'] > 0 else ""
            else:
                faction_discord_text += f".INF +{data[i][0]['Factions'][x]['MissionPoints']}; " if data[i][0]['Factions'][x]['MissionPoints'] > 0 else f".INF {data[i][0]['Factions'][x]['MissionPoints']}; " if data[i][0]['Factions'][x]['MissionPoints'] < 0 else ""
            faction_discord_text += f".BVs {human_format(data[i][0]['Factions'][x]['Bounties'])}; " if data[i][0]['Factions'][x]['Bounties'] != 0 else ""
            faction_discord_text += f".CBs {human_format(data[i][0]['Factions'][x]['CombatBonds'])}; " if data[i][0]['Factions'][x]['CombatBonds'] != 0 else ""
            faction_discord_text += f".Trade {human_format(data[i][0]['Factions'][x]['TradeProfit'])}; " if data[i][0]['Factions'][x]['TradeProfit'] != 0 else ""
            faction_discord_text += f".Expl {human_format(data[i][0]['Factions'][x]['CartData'])}; " if data[i][0]['Factions'][x]['CartData'] != 0 else ""
            faction_discord_text += f".Murders {data[i][0]['Factions'][x]['Murdered']}; " if data[i][0]['Factions'][x]['Murdered'] != 0 else ""
            faction_discord_text += f".Fails {data[i][0]['Factions'][x]['MissionFailed']}; " if data[i][0]['Factions'][x]['MissionFailed'] != 0 else ""
            space_cz = build_cz_text(data[i][0]['Factions'][x].get('SpaceCZ', {}), "SpaceCZs")
            faction_discord_text += f"{space_cz}; " if space_cz != "" else ""
            ground_cz = build_cz_text(data[i][0]['Factions'][x].get('GroundCZ', {}), "GroundCZs")
            faction_discord_text += f"{ground_cz}; " if ground_cz != "" else ""
            faction_name = process_faction_name(data[i][0]['Factions'][x]['Faction'])
            system_discord_text += f"[{faction_name}] - {faction_discord_text}\n" if faction_discord_text != "" else ""

        discord_text += f"```css\n{data[i][0]['System']}\n{system_discord_text}```" if system_discord_text != "" else ""

    return discord_text.replace("'", "")


def process_faction_name(faction_name):
    """
    Shorten the faction name if the user has chosen to
    """
    if this.AbbreviateFactionNames.get() == "Yes":
        return ''.join(i[0] for i in faction_name.split())
    else:
        return faction_name


def build_cz_text(cz_data, prefix):
    """
    Create a summary of Conflict Zone activity
    """
    if cz_data == {}: return ""
    text = ""

    if 'l' in cz_data and cz_data['l'] != '0' and cz_data['l'] != '': text += f"{cz_data['l']}xL "
    if 'm' in cz_data and cz_data['m'] != '0' and cz_data['m'] != '': text += f"{cz_data['m']}xM "
    if 'h' in cz_data and cz_data['h'] != '0' and cz_data['h'] != '': text += f"{cz_data['h']}xH "

    if text != '': text = f".{prefix} {text}"
    return text


def display_todaydata():
    """
    Display the latest tally data window
    """
    display_data("Latest BGS Tally", this.TodayData, Ticks.TICK_CURRENT)


def display_yesterdaydata():
    """
    Display the previous tally data window
    """
    display_data("Previous BGS Tally", this.YesterdayData, Ticks.TICK_PREVIOUS)


def copy_to_clipboard(Form, Discord):
    """
    Get all text from the Discord field and put it in the Copy buffer
    """
    Form.clipboard_clear()
    Form.event_generate("<<TextModified>>")
    Form.clipboard_append(Discord.get('1.0', 'end-1c'))
    Form.update()


def post_to_discord(Form, Discord, tick_mode):
    """
    Get all text from the Discord field and post it to the webhook
    """
    if not is_webhook_valid(): return

    discord_text = Discord.get('1.0', 'end-1c').strip()

    # We store a historical discord message ID for the current and previous ticks, so fetch the right one
    if tick_mode == Ticks.TICK_CURRENT: discord_message_id = this.DiscordCurrentMessageID
    else: discord_message_id = this.DiscordPreviousMessageID

    if discord_message_id.get() == '' or discord_message_id.get() == None:
        # No previous post
        if discord_text != '':
            url = this.DiscordWebhook.get()
            response = requests.post(url=url, params={'wait': 'true'}, data={'content': discord_text, 'username': this.DiscordUsername.get()})
            if response.ok:
                # Store the Message ID
                response_json = response.json()
                discord_message_id.set(response_json['id'])
            else:
                logger.error(f"Unable to create new discord post. Reason: '{response.reason}' Content: '{response.content}' URL: '{url}'")

    else:
        # Previous post, amend or delete it
        if discord_text != '':
            url = f"{this.DiscordWebhook.get()}/messages/{discord_message_id.get()}"
            response = requests.patch(url=url, data={'content': discord_text, 'username': this.DiscordUsername.get()})
            if not response.ok:
                discord_message_id.set('')
                logger.error(f"Unable to update previous discord post. Reason: '{response.reason}' Content: '{response.content}' URL: '{url}'")

                # Try to post new message instead
                url = this.DiscordWebhook.get()
                response = requests.post(url=url, params={'wait': 'true'}, data={'content': discord_text, 'username': this.DiscordUsername.get()})
                if response.ok:
                    # Store the Message ID
                    response_json = response.json()
                    discord_message_id.set(response_json['id'])
                else:
                    logger.error(f"Unable to create new discord post. Reason: '{response.reason}' Content: '{response.content}' URL: '{url}'")
        else:
            url = f"{this.DiscordWebhook.get()}/messages/{discord_message_id.get()}"
            response = requests.delete(url=url)
            if response.ok:
                # Clear the Message ID
                discord_message_id.set('')
            else:
                logger.error(f"Unable to delete previous discord post. Reason: '{response.reason}' Content: '{response.content}' URL: '{url}'")


def is_webhook_valid():
    """
    Do a basic check on the user specified Discord webhook
    """
    return this.DiscordWebhook.get().startswith('https://discord.com/api/webhooks/')


def tick_format(ticktime):
    """
    Format the tick date/time
    """
    datetime_object = datetime.strptime(ticktime, '%Y-%m-%dT%H:%M:%S.%fZ')
    return datetime_object.strftime("%H:%M:%S UTC %A %d %B")


def save_data():
    """
    Save all data structures
    """
    config.set('XLastTick', this.CurrentTick)
    config.set('XTickTime', this.TickTime)
    config.set('XStatus', this.Status.get())
    config.set('XAbbreviate', this.AbbreviateFactionNames.get())
    config.set('XDiscordWebhook', this.DiscordWebhook.get())
    config.set('XDiscordUsername', this.DiscordUsername.get())
    config.set('XDiscordCurrentMessageID', this.DiscordCurrentMessageID.get())
    config.set('XDiscordPreviousMessageID', this.DiscordPreviousMessageID.get())
    config.set('XIndex', this.DataIndex.get())
    config.set('XStation', this.StationFaction.get())
    file = os.path.join(this.Dir, "Today Data.txt")
    with open(file, 'w') as outfile:
        json.dump(this.TodayData, outfile)
    file = os.path.join(this.Dir, "Yesterday Data.txt")
    with open(file, 'w') as outfile:
        json.dump(this.YesterdayData, outfile)
    file = os.path.join(this.Dir, "MissionLog.txt")
    with open(file, 'w') as outfile:
        json.dump(this.MissionLog, outfile)
