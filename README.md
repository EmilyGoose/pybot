# Pybot
Bot for Discord built in Python

This is a side project of mine, which hopefully will make it easy to keep track of ideas my team has for upcoming hackathons.
Feel free to use the code, but please credit me (preferably via direct link to this repo). I try to comment it where possible.
This is still very unstable, so if you would like to make a pull request, please just submit an issue. The master branch is the version built for Slack.

## Breaking changes
Pybot now requires the async branch of discord.py and consequently Python >= 3.4

Incompatible with user accounts, the bot must run on a bot account.
If that's too much hassle for you, [click here](http://bit.ly/getpybot) to rely on our running instance of the bot.

## Usage
Note: All commands must be prefaced with "@pybot"

### idea: \<text\>

Enters an idea. Make sure there is a space after the colon

### getideas \<name\>

Gets an idea. Must be a name, not an @mention. Omit the name parameter to get your own ideas.


### delidea \<*n*\>

Deletes the *n* th idea in your list of ideas. It is recommended to call !getideas first.

### clearideas

Deletes ALL your ideas. Use with caution.

### machineinfo

Displays information about the machine running the bot

### splitchannel

Keeps future ideas from channel separate and private to the channel

### mergechannel

Makes ideas from channel available to other channels

### setresponse "\<*response*\>" for "\<*call*\>"

Has pybot respond with *response* whenever a message matches *call*

### delresponse \<*call*\>

Deletes response for *call*

### getresponses

Gets all responses

### clearresponses

Deletes ALL responses

### getout

Pybot leaves the server :(

(Only the owner can use this)

### help

Displays version info and a list of commands

## Setup instructions

*NOTE: If you would like to add pybot to your server [click here](http://bit.ly/addpybot) instead.*

Unless you REALLY want to run your own bot, you can rely on the instance run by me.


1. Install Python >= 3.4

2. Install the async branch of [discord.py](https://github.com/Rapptz/discord.py/tree/async). You can do this through pip if you have git installed:

...`pip install git+https://github.com/Rapptz/discord.py@async`

3. Set up a Discord bot user (Not a regular user. To set up a bot user [click here](https://discordapp.com/developers/applications/me))

4. Place bot.py in whichever folder you want it to run in.

5. Create a file named "cfg.py" in the same folder. The file should look like this:

```Python
TOKEN = "<redacted>"
DEBUGMODE = False #Or True if you REALLY want
DEBUGCH = "<channel id>" #Isn't entirely necessary if DEBUGMODE is False
KILLERIDS = "<ids>" #Table of people who can force quit the bot
```

Now you're ready to run the bot! If you get any errors you've probably done something wrong in the config file.

## New since v5.0

### Features

* Support for separate servers
* Splitting channel data from the rest of the server
* Responses

### Commands

* clearideas command
* mergechannel command
* splitchannel command
* setresponse command
* delresponse command
* getresponses command
* clearresponses command
* getout command

### Other

* Fixes to command processing
* Fixes to help command
* Compatibility with multiple servers
* Now uses discord.py async branch and works exclusively for bot users
* No more scary error messages
