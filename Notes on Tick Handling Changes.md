Notes on Tick Handling Changes

Need a 'manager' class to manage this subfolder, with cleanup for old files

Activitymanager needs to know about and handle a new tick

Activity should be stored via latest Activity object fetched from ActivityManager



New data storage solution should work completely in parallel with existing - then after a period of testing we can ensure new exactly matches old. Even to the point of generating parallel Discord reports, which should also be identical.

