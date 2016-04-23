# Pybot
Bot for Discord built in Python

This is a side project of mine, which hopefully will make it easy to keep track of ideas my team has for upcoming hackathons.
Feel free to use the code, but please credit me (preferably via direct link to this repo). I try to comment it where possible.
This is still very unstable, so if you would like to make a pull request, please just submit an issue. The master branch is the version built for Slack.

# Usage

### @pybot idea: \<text\>

Enters an idea. Make sure there is a space after the colon


### @pybot getideas \<name\>

Gets an idea. Must be a name, not an @mention. Omit the name parameter to get your own ideas


### @pybot delidea \<*n*\>

Deletes the *n* th idea in your list of ideas. It is recommended to call !getideas first.

### @pybot clearideas

Deletes ALL your ideas. Use with caution.

### @pybot machineinfo

Displays information about the machine running the bot

### @pybot splitchannel

Keeps future ideas from channel separate and private to the channel

### @pybot mergechannel

Makes ideas from channel available to other channels

@pybot setresponse "\<*response*\>" for "\<*call*\>"

Has pybot respond with *response* whenever a message matches *call*

### @pybot help

Displays version info and a list of commands

# Setup instructions

Place bot.py in whichever folder you want it to run in. Note that it creates multiple text files, so putting it in a folder would be recommended.
Create a file named "cfg.py" in the same folder. The file should look like this:

```Python
EMAIL = "<redacted>"
PASSWORD = "<redacted>"
DEBUGMODE = False #Or True if you REALLY want
DEBUGCH = "<channel id>"
BOTID = "<bot Discord ID used in @mentions>"
BOTNAME = "<bot username>"
```

NOTE: Pybot v6 will work for multiple servers and will be able to be added via PM, making running your own instance useless.

# New since v5.0

### Commands

* clearideas command
* mergechannel command
* splitchannel command
* setresponse command

### Other

* Fixes to command processing
* Fixes to help command
