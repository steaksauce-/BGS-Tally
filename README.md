# BGS-Tally (modified by Aussi)

An EDMC plugin to count BGS work

Based on BGS-Tally v2.0 by tezw21: [Original tezw21 BGS-Tally-v2.0 Project](https://github.com/tezw21/BGS-Tally-v2.0)

Modified by Aussi to include Discord-ready information and quick Copy to Clipboard function: [aussig BGS-Tally Project](https://github.com/aussig/BGS-Tally)


# Installation

Download the [latest release](https://github.com/aussig/BGS-Tally/releases/) of BGS Tally
 - In EDMC, on the Plugins settings tab press the _Open_ button. This reveals the EDMC plugins folder where it looks for plugins.
 - Extract the .zip archive that you downloaded, which will create a _BGS-Tally_ folder. Move this folder into your EDMC plugins folder.
 - Re-start EDMC for it to notice the new plugin.
 - In EDMC, go to _File_ -> _Settings_ -> _BGS Tally v2_ and click _Make BGS Tally Active_ to enable the plugin.


# Usage

BGS Tally counts all the BGS work you do for any faction, in any system. 

It is highly recommended that EDMC is started before ED is launched as data is recorded at startup and then when you dock at a station. Not doing this can result in missing data.

The data is shown on a pop up window when the _Data Today_ or _Data Yesterday_ buttons on the EDMC main screen are clicked. The plugin works out what 'Today' and 'Yesterday' are based on the latest tick time as published here: https://elitebgs.app/api/ebgs/v5/ticks and also shows the latest tick time and date on the main EDMC window.

The plugin also generates a nicely formatted 'Discord Ready' text string which can be copied and pasted into a Discord chat. Or just click the handy 'Copy to Clipboard' button.

The plugin can paused / restarted in the BSG Tally tab in settings.

The following activities are counted: 
- Mission inf +
- Total trade profit sold to Faction controlled station
- Cartographic data sold to Faction controlled station
- Bounties issued by named Faction.
- Combat Bonds issued by named Faction
- Missions Failed for named Faction
- Ships murdered owned by named Faction
- Missions are counted when a Faction is in Election. Only missions that my research suggests work during Election are counted, this is a work in progress
- Negative trade is counted with a minus sign in trade profit column.

These total during the session and reset at server tick.
The state column has 3 options, None, War or Election to give an indication on how missions are being counted
