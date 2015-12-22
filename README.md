# Pybot
Bot for Slack built in Python

This is a side project of mine, which hopefully will make it easy to keep track of ideas my team has for upcoming hackathons.

Feel free to use my code, but please credit me (preferably via direct link to this repo). I try to comment it where possible.

If you would like to make a pull request, please make it to "usbot.py". "bot.py" is my stable build.

# Usage

## !idea: \<text\>

Enters an idea. Make sure there is a space after the colon


## !getideas \<name\>

Gets an idea. Make sure the name matches the person's first name (if they haven't set one, their Slack username) as of the bot's last restart.
Make sure there is a space between the command and the person's name.


## !delidea \<*n*\>

Deletes the *n*th idea in your list of ideas. It is reccomended to call !getideas first.

