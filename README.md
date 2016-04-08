# Pybot
Bot for Slack built in Python by Misha Larionov, ported to Discord by Nicholas Carr

This is a side project of mine, which hopefully will make it easy to keep track of ideas my team has for upcoming hackathons.
Feel free to use the code, but please credit me (preferably via direct link to this repo). I try to comment it where possible.
This is still very unstable, so if you would like to make a pull request, please just submit an issue. The master branch is the version built for Slack.

# Usage

### !idea: \<text\>

Enters an idea. Make sure there is a space after the colon


### !getideas \<name\>

Gets an idea. Make sure the name matches the person's first name (if they haven't set one, their Slack username) as of the bot's last restart.
Make sure there is a space between the command and the person's name.


### !delidea \<*n*\>

Deletes the *n*th idea in your list of ideas. It is recommended to call !getideas first.

### !machineinfo

Displays information about the machine running the bot

### !help

Displays version info and a list of commands

# Setup instructions

Place bot.py in whichever folder you want it to run in. Note that it creates multiple text files, so putting it in a folder would be recommended.
Create a file named "cfg.py" in the same folder. The file should look like this:

```Python
EMAIL = "<redacted>"
PASSWORD = "<redacted>"
DEBUGMODE = True
DEBUGCH = "<channel id>"
```

NOTE: Pybot v6 will work for multiple servers and will be able to be added via PM, making running your own instance useless.

# New in v5.0

### Commands
* !help

### New Features
* Works on Discord

### Fixes
* Rewritten from the ground up
