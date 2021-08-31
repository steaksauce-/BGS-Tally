# Change Log

## vx.x.x - xxxx-xx-xx

### Bug Fixes

* Now honour the 'Trend' for mission Influence rewards: `UpGood` and `DownGood` are now treated as *+INF* while `UpBad` and `DownBad` are treated as *-INF*.

### Changes:

* Report both +INF and -INF in Discord message.


### Changes:

* Various improvements to README:
    * Improved installation instructions.
    * Added instructions for upgrading from previous version.
    * Added personal data and privacy section.


## v1.1.0 - 2021-08-31

### Changes:

* Changed 'Missions' to 'INF' in Discord text.
* Removed 'Failed Missions' from Discord text.
* Made windows a bit wider to accommodate longer faction names.
* Changed plugin name to just 'BGS Tally' in settings.
* Improvements to the usage instructions in README.
* Renamed buttons to 'Latest Tick Data' and 'Earlier Tick Data' to more clearly describe what each does, avoiding the use of day-based terms 'Yesterday' and 'Today'.


## v1.0.0 - 2021-08-27

Initial release, based on original [BGS-Tally-v2.0 project by tezw21](https://github.com/tezw21/BGS-Tally-v2.0)

### New features:

* Now creates a Discord-ready string for copying and pasting into a Discord chat.
* _Copy to Clipboard_ button to streamline copying the Discord text.

### Bug fixes:

* Typo in 'Missions' fixed

### Other changes:

* Now logs to the EDMC log file, as per latest EDMC documentation recommendations.
