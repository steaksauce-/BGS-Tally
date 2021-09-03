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
this.VersionNo = "1.1.1"
this.FactionNames = []
this.TodayData = {}
this.YesterdayData = {}
this.DataIndex = 0
this.Status = "Active"
this.TickTime = ""
this.State = tk.IntVar()
this.MissionLog = []
this.MissionListNonViolent = [
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
    'Chain_HelpFinishTheOrder_name']


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


def plugin_prefs(parent, cmdr, is_beta):
    """
    Return a TK Frame for adding to the EDMC settings dialog.
    """
    frame = nb.Frame(parent)
    nb.Label(frame, text="BGS Tally (modified by Aussi) v" + this.VersionNo).grid(column=0, sticky=tk.W)
    nb.Checkbutton(frame, text="Make BGS Tally Active", variable=this.Status, onvalue="Active",
                   offvalue="Paused").grid()
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
    this.DataIndex = tk.IntVar(value=config.get_int("xIndex"))
    this.StationFaction = tk.StringVar(value=config.get_str("XStation"))
    response = requests.get('https://api.github.com/repos/aussig/BGS-Tally/releases/latest')  # check latest version
    latest = response.json()
    this.GitVersion = latest['tag_name']
    #  tick check and counter reset
    response = requests.get('https://elitebgs.app/api/ebgs/v5/ticks')  # get current tick and reset if changed
    tick = response.json()
    this.CurrentTick = tick[0]['_id']
    this.TickTime = tick[0]['time']
    if this.LastTick.get() != this.CurrentTick:
        this.LastTick.set(this.CurrentTick)
        this.YesterdayData = this.TodayData
        this.TodayData = {}
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
    tk.Label(this.frame, text="Status:").grid(row=2, column=0, sticky=tk.W)
    tk.Label(this.frame, text="Last Tick:").grid(row=3, column=0, sticky=tk.W)
    this.StatusLabel = tk.Label(this.frame, text=this.Status.get()).grid(row=2, column=1, sticky=tk.W)
    this.TimeLabel = tk.Label(this.frame, text=tick_format(this.TickTime)).grid(row=3, column=1, sticky=tk.W)
    return this.frame


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
        #  tick check and counter reset
        response = requests.get('https://elitebgs.app/api/ebgs/v5/ticks')  # get current tick and reset if changed
        tick = response.json()
        this.CurrentTick = tick[0]['_id']
        this.TickTime = tick[0]['time']
        if this.LastTick.get() != this.CurrentTick:
            this.LastTick.set(this.CurrentTick)
            this.YesterdayData = this.TodayData
            this.TodayData = {}
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
                                    if this.TodayData[y][0]['Factions'][z]['Faction'] == fe3 and this.TodayData[y][0]['Factions'][z]['FactionState'] == 'Election' and entry['Name'] in this.MissionListNonViolent:
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
        logger.info('Combat Bond redeemed')
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
    # Update data structures not present in previous versions of plugin

    # From < v1.2.0 to 1.2.0
    if not 'SpaceCZ' in faction_data: faction_data['SpaceCZ'] = {}
    if not 'GroundCZ' in faction_data: faction_data['GroundCZ'] = {}


def display_data(title, data):
    """
    Display the data window, using either latest or previous data
    """
    Form = tk.Toplevel(this.frame)
    Form.title("BGS Tally v" + this.VersionNo + " - " + title)
    Form.geometry("1000x700")
    TabParent = ttk.Notebook(Form)
    Discord = tk.Text(Form, wrap = tk.WORD, height=20, font = ("Helvetica", 9))

    for i in data:
        tab = ttk.Frame(TabParent)
        TabParent.add(tab, text=data[i][0]['System'])
        FactionLabel = ttk.Label(tab, text="Faction")
        FactionStateLabel = ttk.Label(tab, text="State")
        MPLabel = ttk.Label(tab, text="INF")
        TPLabel = ttk.Label(tab, text="Trade")
        BountyLabel = ttk.Label(tab, text="BVs")
        CDLabel = ttk.Label(tab, text="Expl")
        CombatLabel = ttk.Label(tab, text="CBs")
        FailedLabel = ttk.Label(tab, text="Fails")
        MurderLabel = ttk.Label(tab, text="Murders")
        SpaceCZsLabel = ttk.Label(tab, text="Space CZs")
        SpaceCZsLabelL = ttk.Label(tab, text="L")
        SpaceCZsLabelM = ttk.Label(tab, text="M")
        SpaceCZsLabelH = ttk.Label(tab, text="H")
        GroundCZsLabel = ttk.Label(tab, text="On-foot CZs")
        GroundCZsLabelL = ttk.Label(tab, text="L")
        GroundCZsLabelM = ttk.Label(tab, text="M")
        GroundCZsLabelH = ttk.Label(tab, text="H")

        FactionLabel.grid(row=0, column=0, padx=2, pady=2)
        FactionStateLabel.grid(row=0, column=1, padx=2, pady=2)
        MPLabel.grid(row=0, column=2, padx=2, pady=2)
        TPLabel.grid(row=0, column=3, padx=2, pady=2)
        BountyLabel.grid(row=0, column=4, padx=2, pady=2)
        CDLabel.grid(row=0, column=5, padx=2, pady=2)
        CombatLabel.grid(row=0, column=6, padx=2, pady=2)
        FailedLabel.grid(row=0, column=7, padx=2, pady=2)
        MurderLabel.grid(row=0, column=8, padx=2, pady=2)
        SpaceCZsLabel.grid(row=0, column=9, columnspan=3, padx=2)
        GroundCZsLabel.grid(row=0, column=12, columnspan=3, padx=2)
        SpaceCZsLabelL.grid(row=1, column=9, padx=2, pady=2)
        SpaceCZsLabelM.grid(row=1, column=10, padx=2, pady=2)
        SpaceCZsLabelH.grid(row=1, column=11, padx=2, pady=2)
        GroundCZsLabelL.grid(row=1, column=12, padx=2, pady=2)
        GroundCZsLabelM.grid(row=1, column=13, padx=2, pady=2)
        GroundCZsLabelH.grid(row=1, column=14, padx=2, pady=2)

        header_rows = 2
        z = len(data[i][0]['Factions'])

        for x in range(0, z):
            update_faction_data(data[i][0]['Factions'][x])

            FactionName = ttk.Label(tab, text=data[i][0]['Factions'][x]['Faction'])
            FactionName.grid(row=x + header_rows, column=0, sticky=tk.W, padx=2, pady=2)
            FactionState = ttk.Label(tab, text=data[i][0]['Factions'][x]['FactionState'])
            FactionState.grid(row=x + header_rows, column=1)
            Missions = ttk.Label(tab, text=data[i][0]['Factions'][x]['MissionPoints'])
            Missions.grid(row=x + header_rows, column=2)
            Trade = ttk.Label(tab, text=human_format(data[i][0]['Factions'][x]['TradeProfit']))
            Trade.grid(row=x + header_rows, column=3)
            Bounty = ttk.Label(tab, text=human_format(data[i][0]['Factions'][x]['Bounties']))
            Bounty.grid(row=x + header_rows, column=4)
            CartData = ttk.Label(tab, text=human_format(data[i][0]['Factions'][x]['CartData']))
            CartData.grid(row=x + header_rows, column=5)
            Failed = ttk.Label(tab, text=data[i][0]['Factions'][x]['MissionFailed'])
            Failed.grid(row=x + header_rows, column=7)
            Combat = ttk.Label(tab, text=human_format(data[i][0]['Factions'][x]['CombatBonds']))
            Combat.grid(row=x + header_rows, column=6)
            Murder = ttk.Label(tab, text=data[i][0]['Factions'][x]['Murdered'])
            Murder.grid(row=x + header_rows, column=8)
            CZSpaceLVar = tk.StringVar(value=data[i][0]['Factions'][x]['SpaceCZ'].get('l', '0'))
            CZSpaceL = ttk.Spinbox(tab, from_=0, to=999, width=3, textvariable=CZSpaceLVar)
            CZSpaceL.grid(row=x + header_rows, column=9, padx=2, pady=2)
            CZSpaceMVar = tk.StringVar(value=data[i][0]['Factions'][x]['SpaceCZ'].get('m', '0'))
            CZSpaceM = ttk.Spinbox(tab, from_=0, to=999, width=3, textvariable=CZSpaceMVar)
            CZSpaceM.grid(row=x + header_rows, column=10, padx=2, pady=2)
            CZSpaceHVar = tk.StringVar(value=data[i][0]['Factions'][x]['SpaceCZ'].get('h', '0'))
            CZSpaceH = ttk.Spinbox(tab, from_=0, to=999, width=3, textvariable=CZSpaceHVar)
            CZSpaceH.grid(row=x + header_rows, column=11, padx=2, pady=2)
            CZGroundLVar = tk.StringVar(value=data[i][0]['Factions'][x]['GroundCZ'].get('l', '0'))
            CZGroundL = ttk.Spinbox(tab, from_=0, to=999, width=3, textvariable=CZGroundLVar)
            CZGroundL.grid(row=x + header_rows, column=12, padx=2, pady=2)
            CZGroundMVar = tk.StringVar(value=data[i][0]['Factions'][x]['GroundCZ'].get('m', '0'))
            CZGroundM = ttk.Spinbox(tab, from_=0, to=999, width=3, textvariable=CZGroundMVar)
            CZGroundM.grid(row=x + header_rows, column=13, padx=2, pady=2)
            CZGroundHVar = tk.StringVar(value=data[i][0]['Factions'][x]['GroundCZ'].get('h', '0'))
            CZGroundH = ttk.Spinbox(tab, from_=0, to=999, width=3, textvariable=CZGroundHVar)
            CZGroundH.grid(row=x + header_rows, column=14, padx=2, pady=2)
            # Watch for changes on all SpinBox Variables. This approach catches any change, including manual editing, while using 'command' callbacks only catches clicks
            CZSpaceLVar.trace('w', partial(cz_change, CZSpaceLVar, Discord, CZs.SPACE_LOW, data, i, x))
            CZSpaceMVar.trace('w', partial(cz_change, CZSpaceMVar, Discord, CZs.SPACE_MED, data, i, x))
            CZSpaceHVar.trace('w', partial(cz_change, CZSpaceHVar, Discord, CZs.SPACE_HIGH, data, i, x))
            CZGroundLVar.trace('w', partial(cz_change, CZGroundLVar, Discord, CZs.GROUND_LOW, data, i, x))
            CZGroundMVar.trace('w', partial(cz_change, CZGroundMVar, Discord, CZs.GROUND_MED, data, i, x))
            CZGroundHVar.trace('w', partial(cz_change, CZGroundHVar, Discord, CZs.GROUND_HIGH, data, i, x))

    Discord.insert(tk.INSERT, generate_discord_text(data))
    # Select all text and focus the field
    Discord.tag_add('sel', '1.0', 'end')
    Discord.focus()

    CopyButton = ttk.Button(Form, text="Copy to Clipboard", command=partial(copy_to_clipboard, Form, Discord))

    TabParent.pack(fill='both', expand=1, side='top', padx=5, pady=5)
    CopyButton.pack(side='bottom', padx=5, pady=5)
    Discord.pack(fill='x', side='bottom', padx=5, pady=5)


def cz_change(CZVar, Discord, cz_type, data, system_index, faction_index, *args):
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


def generate_discord_text(data):
    """
    Generate the Discord-formatted version of the tally data
    """
    discord_text = ""

    for i in data:
        system_discord_text = ""
        z = len(data[i][0]['Factions'])

        for x in range(0, z):
            faction_discord_text = ""
            faction_discord_text += f"_INF_: {data[i][0]['Factions'][x]['MissionPoints']}; " if data[i][0]['Factions'][x]['MissionPoints'] != 0 else ""
            faction_discord_text += f"_BVs_: {human_format(data[i][0]['Factions'][x]['Bounties'])}; " if data[i][0]['Factions'][x]['Bounties'] != 0 else ""
            faction_discord_text += f"_CBs_: {human_format(data[i][0]['Factions'][x]['CombatBonds'])}; " if data[i][0]['Factions'][x]['CombatBonds'] != 0 else ""
            faction_discord_text += f"_Trade_: {human_format(data[i][0]['Factions'][x]['TradeProfit'])}; " if data[i][0]['Factions'][x]['TradeProfit'] != 0 else ""
            faction_discord_text += f"_Expl_: {human_format(data[i][0]['Factions'][x]['CartData'])}; " if data[i][0]['Factions'][x]['CartData'] != 0 else ""
            faction_discord_text += f"_Murders_: {data[i][0]['Factions'][x]['Murdered']}; " if data[i][0]['Factions'][x]['Murdered'] != 0 else ""
            space_cz = build_cz_text(data[i][0]['Factions'][x].get('SpaceCZ', {}), "Space CZs")
            faction_discord_text += f"{space_cz}; " if space_cz != "" else ""
            ground_cz = build_cz_text(data[i][0]['Factions'][x].get('GroundCZ', {}), "On-Foot CZs")
            faction_discord_text += f"{ground_cz}; " if ground_cz != "" else ""

            system_discord_text += f"    **{data[i][0]['Factions'][x]['Faction']}**: {faction_discord_text}\n" if faction_discord_text != "" else ""

        discord_text += f"**{data[i][0]['System']}**: \n{system_discord_text}\n" if system_discord_text != "" else ""

    return discord_text


def build_cz_text(cz_data, prefix):
    """
    Create a summary of Combat Zone activity
    """
    if cz_data == {}: return ""
    text = ""

    if 'l' in cz_data and cz_data['l'] != '0' and cz_data['l'] != '': text += f"{cz_data['l']} x Low "
    if 'm' in cz_data and cz_data['m'] != '0' and cz_data['m'] != '': text += f"{cz_data['m']} x Med "
    if 'h' in cz_data and cz_data['h'] != '0' and cz_data['h'] != '': text += f"{cz_data['h']} x High "

    if text != '': text = f"_{prefix}_: {text}"
    return text


def display_todaydata():
    """
    Display the latest tally data window
    """
    display_data("Latest BGS Tally", this.TodayData)


def display_yesterdaydata():
    """
    Display the previous tally data window
    """
    display_data("Previous BGS Tally", this.YesterdayData)


def copy_to_clipboard(Form, Discord):
    """
    Get all text from the Discord field and put it in the Copy buffer
    """
    Form.clipboard_clear()
    Form.event_generate("<<TextModified>>")
    Form.clipboard_append(Discord.get('1.0', 'end-1c'))
    Form.update()


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
