# BGS-Tally V2.2.0 (modified by Aussi)

An EDMC plugin to count BGS work

Now compatible with Python 3 release

Original version by tezw21 (https://github.com/tezw21/BGS-Tally-v2.0)
Modified by Aussi to include Discord-ready information (https://github.com/aussig/BGS-Tally-v2.0)


# Installation

Download the [latest release](https://github.com/aussig/BGS-Tally-v2.0/releases/) of BGS Tally
 - In EDMC, on the Plugins settings tab press the _Open_ button. This reveals the plugins folder where this app looks for plugins.
 - Open the .zip archive that you downloaded and move the folder contained inside into the plugins folder.
 - Re-start EDMC for it to notice the new plugin
 - Go to _EDMC_ -> _File_ -> _Settings_ -> _BGS Tally v2_ and click _Make BGS Tally Active_ to enable the plugin.


# Usage

BGS Tally v2.0 counts all the BGS work you do for any faction, in any system. 

It is highly recommended that EDMC is started before ED is launched as Data is recorded at startup and then when you dock at a station. Not doing this can result in missing data.

The data is shown on a pop up window when the _Data Today_ or _Data Yesterday_ buttons on the EDMC main screen are clicked. The plugin works out what 'Today' and 'Yesterday' are based on the latest tick time as published here: https://elitebgs.app/api/ebgs/v5/ticks

The plugin also generates a nicely formatted 'Discord Ready' text string which can be copied and pasted into a Discord chat. Or just click the handy 'Copy to Clipboard' button.

The plugin can paused in the BSG Tally v2.0 tab in settings.

From v2.2 we count the following activities. 
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
