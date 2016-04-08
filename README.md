# Pybot
Bot for Slack built in Python

NOTE: Abandoned in favor of Discord version

This is a side project of mine, which hopefully will make it easy to keep track of ideas my team has for upcoming hackathons.
Feel free to use my code, but please credit me (preferably via direct link to this repo). I try to comment it where possible.
If you would like to make a pull request, please make it to the "unstable" branch. The master branch is my stable build.

# Usage

### !idea: \<text\>

Enters an idea. Make sure there is a space after the colon


### !getideas \<name\>

Gets an idea. Make sure the name matches the person's first name (if they haven't set one, their Slack username) as of the bot's last restart.
Make sure there is a space between the command and the person's name.


### !delidea \<*n*\>

Deletes the *n*th idea in your list of ideas. It is reccommended to call !getideas first.

### !machineinfo

Displays information about the machine running the bot

### !uptime

Displays information about how long the bot instance has been running

# Setup instructions

Place bot.py in whichever folder you want it to run in. Note that it creates multiple text files, so putting it in a folder would be recommended.
Create a file named "cfg.py" in the same folder. The file should look like this:

```Python
TOKEN = "<redacted>"
USTOKEN = "<redacted>"
CHANNEL = "ideas"
DEBUGMODE = True
DEBUGCH = "pybotdebug"
```

Note that you only need the USTOKEN variable if you will be running the unstable build. If DEBUGMODE is set to False, you do not need to set DEBUGCH

# New since v3.3

### Commands
* !uptime (see above)

### New Features
* Channel for bot to listen/post is now configurable
* Debug mode is optional and the debug channel is configurable

### Fixes
* Less hardcoding
* Some shuffling around of code
