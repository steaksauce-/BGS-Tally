# Change Log

## vx.x.x - xxxx-xx-xx

### Bug Fixes:

* Never track on-foot CZs when in Horizons, to help reduce false positives.

### Changes:

* Faction name abbreviations are slightly better when dealing with numbers, as they are no longer abbreviated. For example `Nobles of LTT 420` is now shortened to `NoL420` instead of `NoL4`.


## v1.7.1 - 2021-12-21

### Bug Fixes:

* Fix plugin failure if tick happens while in-game, and you try to hand in BGS work before jumping to another system.


## v1.7.0 - 2021-11-01

### New Features:

* Now track (and report) names of on-foot CZs fought at, automatically determine CZ Low / Med / High, and automatically increment counts. Note that we still can't determine whether you've actually _won_ the CZ, so we count it as a win if you've fought there.
* Now track Exobiology data sold.
* New setting to show/hide tabs for systems that have no BGS activity, default to show.

### Changes:

* Bounty vouchers redeemed on Fleet Carriers now count only 50% of the value.
* Added scrollbar to Discord report.
* When plugin is launched for the very first time, default it to 'Enabled' so it's immediately active.
* Reorganisation and tidy up of settings panel, and add link to help pages.
* The Discord text field and fields in the settings panel now have right-click context menus to Copy, Paste etc.


## v1.6.0 - 2021-10-03

### New Features:

* Now count primary and secondary mission INF separately: Primary INF is for the original mission giving faction and secondary INF is for any target faction(s) affected by the mission. An option is included to exclude secondary INF from the Discord report *
* Discord options are now shown on the main tally windows as well as in the settings.

### Bug Fixes:

* Only count `War` or `Civilwar` missions for the originating faction (thanks @RichardCsiszarik for diagnosing and fixing this).

### Changes:

* Added on-foot scavenger missions and on-foot covert assassination missions to those that count when in `War` or `CivilWar` states.
* Tweaks to window layouts and wording.
* No longer allow mouse wheel to change field values, to help avoid accidental changes.
* Since Odyssey update 7, +INF is now reported for missions for factions in `Election`, `War` and `CivilWar` states. We still report this +INF separately from normal +INF, but have changed the wording to `ElectionINF` / `WarINF` instead of `ElectionMissions` and `WarMissions`.

_* Note that the plugin only tracks primary and secondary INF from this version onwards - all INF in older reports will still be categorised as primary INF._


## v1.5.0 - 2021-09-16

### New features:

* Now count and report certain mission types for factions in the `War` or `CivilWar` states, similarly to how some mission types in `Election` state are counted (gathering a full list of mission types that count when the faction is in conflict is still a work in progress).
* If faction is in state `Election`, `War` or `CivilWar`, don't report fake +INF, instead state the number of election / war missions completed, to avoid confusion.

### Changes:

* Tweaks to window layouts and wording.


## v1.4.0 - 2021-09-09

### New features:

* Can integrate directly with Discord to post messages to a channel, using a user-specified Discord webhook.
* Prefix positive INF with '+'.
* Mission INF is now manually editable as well as automatically updated.
* 'Select all' / 'Select none' checkbox at the top of each system to quickly enable / disable all factions for a system.
* Added 'Failed Missions' to Discord text.

### Bug Fixes:

* Apostrophes in Discord text no longer breaks the colouring.


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
