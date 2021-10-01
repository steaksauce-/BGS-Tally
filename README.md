# BGS-Tally (modified by Aussi)

An [EDMC](https://github.com/EDCD/EDMarketConnector) plugin to count Background Simulation (BGS) work. BGS Tally counts all the BGS work you do for any faction, in any system.

Based on BGS-Tally v2.0 by tezw21: [Original tezw21 BGS-Tally-v2.0 Project](https://github.com/tezw21/BGS-Tally-v2.0)

This modified version includes manual Combat Zone tracking, Discord-ready information, quick Copy to Clipboard function for the Discord text and posting directly to Discord.


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

The data is shown on a pop up window when the _Latest BGS Tally_ or _Previous BGS Tally_ buttons on the EDMC main screen are clicked - data collected since the latest tick in _Latest BGS Tally_ and data from your previous play session before the latest tick in _Previous BGS Tally_. The tick time it uses is published here: https://elitebgs.app/api/ebgs/v5/ticks and the plugin displays this on the main EDMC window for reference.

The plugin also generates a nicely formatted 'Discord Ready' text string which can be copied and pasted into a Discord chat, or posted directly to a Discord channel if you wish (see 'Discord Integration' below for instructions).

The plugin can be paused / restarted by un-checking / checking the _&#9745; Make BGS Tally Active_ checkbox in _File_ &rarr; _Settings_ &rarr; _BGS Tally_.


# What is Tracked

The plugin includes both automatic and manual tracking of data. All automatic and manual data is totalled during the _Latest Tick Data_ session and transferred to _Earlier Tick Data_ at server tick.

## Automatic Stuff

The following activities are automatically collected from your in-game activity:

- Mission INF +++ *
- Election / War / CivilWar mission count †
- Total trade profit sold to Faction controlled station
- Cartographic data sold to Faction controlled station
- Bounties issued by named Faction
- Combat Bonds issued by named Faction
- Missions Failed for named Faction
- Ships murdered owned by named Faction
- Negative trade is counted with a minus sign in trade profit column

_* The plugin tracks primary `INF` (for the mission giving faction) and secondary `INF` (for other factions) separately. Secondary `INF` can be excluded from reports if desired._

_† The plugin will honor `INF` values if they are present for completed missions in the player journal. However, if no `INF` value is reported and the faction is in Elections, non-violent mission types are counted and reported. Similarly if no `INF` value is reported and the faction is at War or Civil War, violent mission types are counted and reported. Gathering a full list of mission types that count towards victory is still a work in progress. Note this may all be obsolete since Odyssey patch 7, as it now apparently reports +INF in all circumstances (yet to be fully confirmed)._

The `State` column shows each faction state to give an indication on how missions are being counted.

All the above are totalled during the _Latest BGS Tally_ session and transfer to _Previous BGS Tally_ at server tick.

## Manual Stuff

The plugin also includes manual tracking of Combat Zones (CZs).  CZs are not included in Elite's Player Journal, so there is no way of automatically working out which CZs you have completed. There are fields for each category of CZ that you can manually change, and these values are incorporated into the Discord text report.


# Discord Integration

The plugin generates Discord-ready text for copying-and-pasting manually into Discord. However, as of v1.4.0, it also now supports direct posting into Discord using a webhook. You will need to create this webhook on your Discord server first. The steps are as follows:

1. In your Discord server, click the Cog / Gear icon &#9881; alongside the channel name.
2. In the menu that appears, click _Integrations_.
3. In the Webhooks panel, click _Create Webhook_.  (If you have any webhooks already set up on the channel, instead click _View Webhooks_ and then _New Webhook_).
4. In the _Name_ field, give your webhook a name, for example 'BGS Tally' would be sensible.
5. Click _Copy Webhook URL_.
6. In EDMC, go to _File_ &rarr; _Settings_ &rarr; _BGS Tally_ and paste the Webhook URL into the _Discord Webhook URL_ field.
7. Optionally, you can also set a username that the Discord post will appear as - type this into the _Discord Post as User_ field. It would be sensible to type in your Discord username, but you can use anything you like.

Once the connection is configured, a new button will appear on the BGS Tally windows titled _Post to Discord_. This will automatically send your report to your Discord server via the Webhook you have configured.

If you post again within the same tick, the plugin will **update** your previous post, rather than creating a second post.


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
