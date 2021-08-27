# BGS-Tally (modified by Aussi)

An [EDMC](https://github.com/EDCD/EDMarketConnector) plugin to count Background Simulation (BGS) work. BGS Tally counts all the BGS work you do for any faction, in any system. 

Based on BGS-Tally v2.0 by tezw21: [Original tezw21 BGS-Tally-v2.0 Project](https://github.com/tezw21/BGS-Tally-v2.0)

Modified by Aussi to include Discord-ready information and quick Copy to Clipboard function.


# Installation

Download the [latest release](https://github.com/aussig/BGS-Tally/releases/) of BGS Tally. Then:

 1. Launch EDMC.
 2. In EDMC, in _File_ &rarr; _Settings_ &rarr; _Plugins_, press the _Open_ button. This reveals the EDMC plugins folder where it looks for plugins.
 3. Extract the .zip archive that you downloaded, which will create a _BGS-Tally_ folder. Move this folder into your EDMC plugins folder.
 4. Re-start EDMC for it to notice the new plugin.
 5. In EDMC, go to _File_ &rarr; _Settings_ &rarr; _BGS Tally_ and click _&#9745; Make BGS Tally Active_ to enable the plugin.


# Usage

It is highly recommended that EDMC is started before ED is launched as data is recorded at startup and then when you dock at a station. Not doing this can result in missing data.

The data is shown on a pop up window when the _Data Today_ or _Data Yesterday_ buttons on the EDMC main screen are clicked. The plugin works out what `Today` and `Yesterday` are based on the latest tick time as published here: https://elitebgs.app/api/ebgs/v5/ticks and also shows the latest tick time and date on the main EDMC window.

The plugin also generates a nicely formatted 'Discord Ready' text string which can be copied and pasted into a Discord chat - just click the handy _Copy to Clipboard_ button at the bottom of the _Data Today_ and _Data Yesterday_ windows.

The plugin can be paused / restarted by un-checking / checking the _&#9745; Make BGS Tally Active_ checkbox in _File_ &rarr; _Settings_ &rarr; _BGS Tally_.

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

All the above are totalled during the _Today_ session and transfer to _Yesterday_ at server tick.

The `State` column has 3 options, `None`, `War` or `Election` to give an indication on how missions are being counted
