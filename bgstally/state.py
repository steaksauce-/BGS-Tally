import tkinter as tk
from typing import Dict

from config import config

from bgstally.enums import CheckStates


class State:
    """
    Manage plugin user state and preferences
    """

    def __init__(self, bgstally):
        self.bgstally = bgstally
        self.load()


    def load(self):
        """
        Load our state
        """
        # UI preference fields
        self.Status:str = tk.StringVar(value=config.get_str('XStatus', default="Active"))
        self.ShowZeroActivitySystems:str = tk.StringVar(value=config.get_str('XShowZeroActivity', default=CheckStates.STATE_ON))
        self.AbbreviateFactionNames:str = tk.StringVar(value=config.get_str('XAbbreviate', default=CheckStates.STATE_OFF))
        self.IncludeSecondaryInf:str = tk.StringVar(value=config.get_str('XSecondaryInf', default=CheckStates.STATE_ON))
        self.DiscordBGSWebhook:str = tk.StringVar(value=config.get_str('XDiscordWebhook'))
        self.DiscordUsername:str = tk.StringVar(value=config.get_str('XDiscordUsername'))
        self.DiscordFCJumpWebhook:str = tk.StringVar(value=config.get_str("XDiscordFCJumpWebhook"))

        # Persistent values
        self.current_system_id:str = config.get_str('XCurrentSystemID')
        self.station_faction:str = config.get_str('XStationFaction')
        self.station_type:str = config.get_str('XStationType')

        # Non-persistent values
        self.last_settlement_approached:Dict = {}
        self.last_ship_targeted:Dict = {}


    def save(self):
        """
        Save our state
        """

        # UI preference fields
        config.set('XStatus', self.Status.get())
        config.set('XShowZeroActivity', self.ShowZeroActivitySystems.get())
        config.set('XAbbreviate', self.AbbreviateFactionNames.get())
        config.set('XSecondaryInf', self.IncludeSecondaryInf.get())
        config.set('XDiscordWebhook', self.DiscordBGSWebhook.get())
        config.set('XDiscordUsername', self.DiscordUsername.get())
        config.set('XDiscordFCJumpWebhook', self.DiscordFCJumpWebhook.get())

        # Persistent values
        config.set('XCurrentSystemID', self.current_system_id if self.current_system_id != None else "")
        config.set('XStationFaction', self.station_faction if self.station_faction != None else "")
        config.set('XStationType', self.station_type if self.station_type != None else "")
