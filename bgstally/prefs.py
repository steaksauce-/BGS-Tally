import tkinter as tk

from config import config

from bgstally.enums import CheckStates


class Prefs:
    """
    Manage plugin user preferences
    """

    def __init__(self):
        self.load()


    def load(self):
        """
        Load our preferences
        """
        self.Status = tk.StringVar(value=config.get_str('XStatus', default="Active"))
        self.ShowZeroActivitySystems = tk.StringVar(value=config.get_str('XShowZeroActivity', default=CheckStates.STATE_ON))
        self.AbbreviateFactionNames = tk.StringVar(value=config.get_str('XAbbreviate', default=CheckStates.STATE_OFF))
        self.IncludeSecondaryInf = tk.StringVar(value=config.get_str('XSecondaryInf', default=CheckStates.STATE_ON))
        self.DiscordWebhook = tk.StringVar(value=config.get_str('XDiscordWebhook'))
        self.DiscordUsername = tk.StringVar(value=config.get_str('XDiscordUsername'))

        self.DiscordCurrentMessageID = tk.StringVar(value=config.get_str('XDiscordCurrentMessageID'))
        self.DiscordPreviousMessageID = tk.StringVar(value=config.get_str('XDiscordPreviousMessageID'))
        self.DataIndex = tk.IntVar(value=config.get_int('xIndex'))
        self.StationFaction = tk.StringVar(value=config.get_str('XStation'))
        self.StationType = tk.StringVar(value=config.get_str('XStationType'))


    def save(self):
        """
        Save our preferences
        """
        config.set('XStatus', self.Status.get())
        config.set('XShowZeroActivity', self.ShowZeroActivitySystems.get())
        config.set('XAbbreviate', self.AbbreviateFactionNames.get())
        config.set('XSecondaryInf', self.IncludeSecondaryInf.get())
        config.set('XDiscordWebhook', self.DiscordWebhook.get())
        config.set('XDiscordUsername', self.DiscordUsername.get())

        config.set('XDiscordCurrentMessageID', self.DiscordCurrentMessageID.get())
        config.set('XDiscordPreviousMessageID', self.DiscordPreviousMessageID.get())
        config.set('XIndex', self.DataIndex.get())
        config.set('XStation', self.StationFaction.get())
        config.set('XStationType', self.StationType.get())