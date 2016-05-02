# Pybot
Bot for Slack built in Python by Misha Larionov, ported to Discord by Nicholas Carr

This is a side project of mine, which hopefully will make it easy to keep track of ideas my team has for upcoming hackathons.
Feel free to use the code, but please credit me (preferably via direct link to this repo). I try to comment it where possible.
This is still very unstable, so if you would like to make a pull request, please just submit an issue. The master branch is the version built for Slack.

## Breaking changes
Pybot now requires the async branch of discord.py and consequently Python >= 3.4
Pybot now requires github3.py and there is a new line you need to add to your cfg

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

### whatis \<*query*\>

Returns a summary of the Wikipedia page for *query*

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

   `pip install git+https://github.com/Rapptz/discord.py@async`

3. Install the following libraries (`pip install <name>`). Alternatively, run dependencyInstaller.py

  * asyncio
  * requests
  * dateparser
  * wikipedia
  * github3.py

4. Set up a Discord bot user (Not a regular user. To set up a bot user [click here](https://discordapp.com/developers/applications/me))

5. Place bot.py in whichever folder you want it to run in.

6. Create a file named "cfg.py" in the same folder. The file should look like this:

```Python
TOKEN = "<redacted>"
KILLERIDS = "<ids>" #Table of people who can force quit the bot
GITHUBCHANNEL = "<channel id where you want GitHub notifications>" #Remove these last two lines to disable GitHub integration
REPOS = [["owner", "repo"], ["MishaLarionov", "pybot"]] #One, none or many
```

Now you're ready to run the bot! If you get any errors you've probably done something wrong in the config file.

## New since 6.0

### Features

* Preliminary GitHub notifications
