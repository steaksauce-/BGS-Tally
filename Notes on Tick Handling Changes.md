Notes on Tick Handling Changes

Currently, the tick_id is only stored in plugin state, not in the saved (Today, Yesterday) data files

Implement a new data file format that is not tied to 'today' and 'yesterday', and includes tick ID and also Discord message IDs, so we can go back to any past tick data if we wish

Need to store these in a subfolder

Need a 'manager' class to manage this subfolder, with cleanup for old files

File name = tick ID?  How do we know which is the latest tick?  Perhaps that's still in plugin state...

Need to store dates in activity data I think - then we can identify the last and previous

Does Activitymanager need to know about and handle new tick?