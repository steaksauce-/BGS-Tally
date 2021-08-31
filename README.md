# BGS-Tally (modified by Aussi)

An [EDMC](https://github.com/EDCD/EDMarketConnector) plugin to count Background Simulation (BGS) work. BGS Tally counts all the BGS work you do for any faction, in any system. 

Based on BGS-Tally v2.0 by tezw21: [Original tezw21 BGS-Tally-v2.0 Project](https://github.com/tezw21/BGS-Tally-v2.0)

Modified by Aussi to include Discord-ready information and quick Copy to Clipboard function.


# Installation

Download the [latest release](https://github.com/aussig/BGS-Tally/releases/) of BGS Tally - it's the file titled _BGS-Tally.zip_. Then:

 1. Launch EDMC.
 2. In EDMC, in _File_ &rarr; _Settings_ &rarr; _Plugins_, press the _Open_ button. This reveals the EDMC plugins folder where it looks for plugins.
 3. Extract the _BGS-Tally.zip_ archive that you downloaded, which will create a _BGS-Tally_ folder. Move this folder into your EDMC plugins folder.
 4. Re-start EDMC for it to notice the new plugin.
 5. In EDMC, go to _File_ &rarr; _Settings_ &rarr; _BGS Tally_ and click _&#9745; Make BGS Tally Active_ to enable the plugin.


# Updating from a Previous Version

The plugin writes your activity to three files in the _BGS-Tally_ folder, so if you want it to keep your progress, before replacing your old _BGS-Tally_ folder with the new one,  move these three files across from old to new:

1. `Today.txt`
2. `Yesterday.txt`
3. `MissionLog.txt`


# Usage

It is highly recommended that EDMC is started before ED is launched as data is recorded at startup and then when you dock at a station. Not doing this can result in missing data.

The data is shown on a pop up window when the _Latest Tick Data_ or _Earlier Tick Data_ buttons on the EDMC main screen are clicked - data collected since the latest tick in _Latest Tick Data_ and data from your previous play session before the latest tick in _Earlier Tick Data_. The tick time it uses is published here: https://elitebgs.app/api/ebgs/v5/ticks and the plugin displays this on the main EDMC window for reference.

The plugin also generates a nicely formatted 'Discord Ready' text string which can be copied and pasted into a Discord chat - just click the handy _Copy to Clipboard_ button at the bottom of the _Latest Tick Data_ and _Earlier Tick Data_ windows.

The plugin can be paused / restarted by un-checking / checking the _&#9745; Make BGS Tally Active_ checkbox in _File_ &rarr; _Settings_ &rarr; _BGS Tally_.


# What is Tracked

The following activities are counted:

- Mission INF +++ *
- Total trade profit sold to Faction controlled station
- Cartographic data sold to Faction controlled station
- Bounties issued by named Faction
- Combat Bonds issued by named Faction
- Missions Failed for named Faction
- Ships murdered owned by named Faction
- Negative trade is counted with a minus sign in trade profit column

_* The plugin will honor `INF` values if they are present for completed missions in the player journal. However, if no `INF` value is reported, certain mission types are still counted as +1 `INF` when a Faction is in Election. Only missions that [tezw21](https://github.com/tezw21/BGS-Tally-v2.0)'s research suggests work during Election are counted, this is a work in progress._

All the above are totalled during the _Latest Tick Data_ session and transfer to _Earlier Tick Data_ at server tick.

The `State` column has 3 options, `None`, `War` or `Election` to give an indication on how missions are being counted


# Your Personal Activity and Privacy

If you're concerned about the privacy of your BGS activity, note that this plugin only tracks your activity locally on your computer - it **does not send your data anywhere else**. It writes the following three files, all in the BGS-Tally folder:

1. `Today.txt` - This contains your activity since the last tick.
2. `Yesterday.txt` - This contains your activity in your previous session before the last tick.
3. `MissionLog.txt` - This contains your currently active list of missions.

All three of these files use the JSON format, so can be easily viewed in a text editor or JSON viewer.

The plugin makes the following two network connections:

1. To [EliteBGS](https://elitebgs.app/api/ebgs/v5/ticks) to grab the date and time of the lastest tick.
2. To [GitHub](https://api.github.com/repos/aussig/BGS-Tally/releases/latest) to check the version of the plugin to see whether there is a newer version available.
