# Change Log

## vx.x.x - xxxx-xx-xx

### New features:

* Can integrate directly with Discord to post messages to a channel, using a user-specified Discord webhook.
* Prefix positive INF with '+'.
* Mission INF is now manually editable as well as automatically updated.
* 'Select all' / 'Select none' checkbox at the top of each system to quickly enable / disable all factions for a system.
* Added 'Failed Missions' to Discord text.

## Bug Fixes:

* Apostrophes in faction names no longer break the colouring.


## v1.3.0 - 2021-09-06

### New features:

* Conflict Zone options are now only presented for factions in `CivilWar` or `War` states.
* The option is now provided to omit individual factions from the report.
* There is a new option in the settings panel to switch on shortening of faction names to their abbreviations. This makes the report less readable but more concise.
* As a suggestion from a user (thanks CMDR Strasnylada!), we now use CSS coloured formatting blocks in the Discord text, which makes it look cleaner and clearer.

### Changes:

* The on-screen layout of the tally table has been improved.


## v1.2.0 - 2021-09-03

### New features:

* Ability to manually add High, Medium and Low on-foot and in-space Combat Zone wins to the Discord report by clicking on-screen buttons.

### Changes:

* Now include a lot more non-violent mission types when counting missions for a faction in the `Election` state (gathering a full list of non-violent mission types is still a work in progress).
* Improvements to layout of window.
* Rename buttons and windows to 'Latest BGS Tally' and 'Previous BGS Tally'.
* The last tick date and time presentation has been improved.


## v1.1.1 - 2021-08-31

### Bug Fixes:

* Now honour the 'Trend' for mission Influence rewards: `UpGood` and `DownGood` are now treated as *+INF* while `UpBad` and `DownBad` are treated as *-INF*.

### Changes:

* Report both +INF and -INF in Discord message.
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
