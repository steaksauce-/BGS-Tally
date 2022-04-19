# BGS-Tally (modified by Aussi)

An [EDMC](https://github.com/EDCD/EDMarketConnector) plugin to count Background Simulation (BGS) work. BGS Tally counts all the BGS work you do for any faction, in any system.

Based on BGS-Tally v2.0 by tezw21: [Original tezw21 BGS-Tally-v2.0 Project](https://github.com/tezw21/BGS-Tally-v2.0)

This modified version includes automatic on-foot Conflict Zone tracking (with settlement names), manual in-space Conflict Zone tracking, Discord-ready information, quick Copy to Clipboard function for the Discord text and posting directly to Discord.


# Initial Installation and Use

Full instructions for **installation and use are [here in the wiki &rarr;](https://github.com/aussig/BGS-Tally/wiki)**.


# Updating from a Previous Version

The plugin writes your activity to three files in the _BGS-Tally_ folder, so if you want it to keep your progress, before replacing your old _BGS-Tally_ folder with the new one,  move these three files across from old to new:

1. `Today.txt`
2. `Yesterday.txt`
3. `MissionLog.txt`


# Discord Integration

The plugin generates Discord-ready text for copying-and-pasting manually into Discord and also supports direct posting into a Discord server of your choice using a webhook. You will need to create this webhook on your Discord server first - **instructions for setting up the webhook within Discord are [here in the wiki &rarr;](https://github.com/aussig/BGS-Tally/wiki/Discord-Server-Setup)**.


# What is Tracked

The plugin includes both automatic and manual tracking of data. All automatic and manual data is totalled during the _Latest Tick Data_ session and transferred to _Earlier Tick Data_ at server tick.

## Automatic Stuff

The following activities are automatically collected from your in-game activity:

- Primary Mission INF +++
- Secondary Mission INF +++ *
- Election / War / CivilWar mission count †
- Total trade purchases
- Total trade profit; negative trade is counted with a minus sign in trade profit column
- Black Market trade profit; negative trade is counted with a minus sign in black market trade profit column
- Cartographic data
- Exobiology data ‡
- Bounties issued by named Faction
- Combat Bonds issued by named Faction
- Missions Failed for named Faction
- Ships murdered owned by named Faction
- On-foot Conflict Zones and settlement names fought at ¶

<span style="font-size:0.75em;">_* The plugin tracks primary `INF` (for the mission giving faction) and secondary `INF` (for other factions) separately. Secondary `INF` can be excluded from reports if desired._</span>

<span style="font-size:0.75em;">_† The plugin will honor `INF` values if they are present for completed missions in the player journal. However, if no `INF` value is reported and the faction is in Elections, non-violent mission types are counted and reported. Similarly if no `INF` value is reported and the faction is at War or Civil War, violent mission types are counted and reported. Gathering a full list of mission types that count towards victory is still a work in progress. Note this may all be obsolete since Odyssey patch 7, as it now apparently reports +INF in all circumstances (yet to be fully confirmed)._</span>

<span style="font-size:0.75em;">_‡ Exobiology data is not currently thought to have any impact on the BGS, but it's reported for reference and future-proofing._</span>

<span style="font-size:0.75em;">_¶ The plugin will attempt to automatically determine the type of on-foot CZs and count them. However, there is no way of knowing whether you have won a CZ, so we assume you'll win and count the CZ if you fight there._</span>

## Manual Stuff

The plugin also includes manual tracking of in-space Conflict Zones (CZs) and Megaship / Space Installation Scenarios.  Neither of these are included in Elite's Player Journal, so there is no way of automatically working out whether Scenarios or CZs have been fought at. There are fields for Scenarios and for each category of CZ that you can manually change, and these values are incorporated into the Discord text report.


# Your Personal Activity and Privacy

If you're concerned about the privacy of your BGS activity, note that this plugin **does not send your data anywhere, unless you specifically choose to by configuring the Discord Integration** (see above for instructions).

It writes the following three files, all in the BGS-Tally folder:

1. `Today.txt` - This contains your activity since the last tick.
2. `Yesterday.txt` - This contains your activity in your previous session before the last tick.
3. `MissionLog.txt` - This contains your currently active list of missions.

All three of these files use the JSON format, so can be easily viewed in a text editor or JSON viewer.

The plugin makes the following network connections:

1. To [EliteBGS](https://elitebgs.app/api/ebgs/v5/ticks) to grab the date and time of the lastest tick.
2. To [GitHub](https://api.github.com/repos/aussig/BGS-Tally/releases/latest) to check the version of the plugin to see whether there is a newer version available.
3. **Only if configured by you** to a specific Discord webhook on a Discord server of your choice, and only when you explicitly click the _Post to Discord_ button.
