import tkinter as tk

from config import config

from bgstally.enums import CheckStates


class State:
    """
    Manage plugin user state and preferences
    """

    def __init__(self):
        self.load()


    def load(self):
        """
        Load our state
        """

        # UI preference fields
        self.Status = tk.StringVar(value=config.get_str('XStatus', default="Active"))
        self.ShowZeroActivitySystems = tk.StringVar(value=config.get_str('XShowZeroActivity', default=CheckStates.STATE_ON))
        self.AbbreviateFactionNames = tk.StringVar(value=config.get_str('XAbbreviate', default=CheckStates.STATE_OFF))
        self.IncludeSecondaryInf = tk.StringVar(value=config.get_str('XSecondaryInf', default=CheckStates.STATE_ON))
        self.DiscordWebhook = tk.StringVar(value=config.get_str('XDiscordWebhook'))
        self.DiscordUsername = tk.StringVar(value=config.get_str('XDiscordUsername'))

        # Other persistent values
        self.StationFaction = config.get_str('XStation')
        self.StationType = config.get_str('XStationType')


    def save(self):
        """
        Save our state
        """

        # UI preference fields
        config.set('XStatus', self.Status.get())
        config.set('XShowZeroActivity', self.ShowZeroActivitySystems.get())
        config.set('XAbbreviate', self.AbbreviateFactionNames.get())
        config.set('XSecondaryInf', self.IncludeSecondaryInf.get())
        config.set('XDiscordWebhook', self.DiscordWebhook.get())
        config.set('XDiscordUsername', self.DiscordUsername.get())

        # Other persistent values
        config.set('XStation', self.StationFaction)
        config.set('XStationType', self.StationType)