Current commands list:
    start - Starts dialog with member
    help - Same as start
    menu - Shows a menu and adds command buttons
    timer - Timer for 5 secs. For group/channel admins only
    json - Returns json file with Steam new releases
    plot - Returns picture of diagram: Game tags usability in new trending games
    analytics - Prints simple analytics using information about Steam New Trending Releases
    get_html - Have 1 arguments. To see hints print "/get_html help"

/timer commands works only in groups and channels (if you are administrator or creator)

In file config.py you set TOKEN of your telegram bot.

If you can't connect to https://api.telegram.com (404 Not found) then decomment dictionary apihelper.proxy in main.py