from os import listdir, mkdir, path, remove
import json
from bgstally.activity import Activity

FILE_LEGACY_CURRENTDATA = 'Today Data.txt'
FILE_LEGACY_PREVIOUSDATA = 'Yesterday Data.txt'
TICKID_LEGACY_PREVIOUS = 'legacy_unknown_previous_tickid'
FOLDER_ACTIVITYDATA = "activitydata"
FILE_SUFFIX = ".json"


class ActivityManager:
    """
    Handles data storage of Activity logs
    """
    def __init__(self, plugindir, current_tickid, logger):
        self.plugindir = plugindir
        self.logger = logger
        self.activitydata = {}
        self.currentactivity = None
        self.previousactivity = None

        self._load(current_tickid)

    def save(self):
        """
        Save all activity data
        """
        for tickid, activity in self.activitydata.items():
            activity.save(path.join(self.plugindir, FOLDER_ACTIVITYDATA, tickid + FILE_SUFFIX))


    def _load(self, current_tickid):
        """
        Load all activity data
        """
        # Handle modern data from subfolder
        filepath = path.join(self.plugindir, FOLDER_ACTIVITYDATA)
        if not path.exists(filepath): mkdir(filepath)
        for activityfilename in listdir(filepath):
            if activityfilename.endswith(FILE_SUFFIX):
                activity = Activity(self.plugindir, self.logger)
                activity.load(path.join(filepath, activityfilename))
                self.activitydata[activity.tickid] = activity

        # Handle legacy data if it exists - parse and migrate to new format
        filepath = path.join(self.plugindir, FILE_LEGACY_CURRENTDATA)
        if path.exists(filepath): self._convert_legacy_data(filepath, current_tickid)
        filepath = path.join(self.plugindir, FILE_LEGACY_PREVIOUSDATA)
        if path.exists(filepath): self._convert_legacy_data(filepath, TICKID_LEGACY_PREVIOUS)


    def _convert_legacy_data(self, filepath, tickid):
        """
        Convert a legacy activity data file to new location and format
        """
        existingactivity = self.activitydata.get(tickid)
        if existingactivity != None:
            # We already have modern data for this legacy tick ID, ignore it and delete the file
            self.logger.warning(f"Tick data already exists for tick {tickid} when loading legacy data. Ignoring legacy data.")
            # TODO: remove(filepath)
            return

        activity = Activity(self.plugindir, self.logger, tickid)
        activity.load_legacy_data(filepath)
        self.activitydata[tickid] = activity

        self.logger.info(f"Loaded Legacy Activity Data for tick {tickid}: {activity.data}")