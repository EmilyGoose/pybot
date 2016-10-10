# Pybot discord-unstable build
# Misha Larionov and Nicholas Carr
# github.com/MishaLarionov/pybot/tree/discord-unstable
# Licensed under MIT License
# See license.txt for full license

# TODO:
# Move responses into a separate .py file

print("Loading... (This may take a while)")

#Import all the stuff
import cfg, time, platform, ast, sys, os, re
#Second line of import statements. These may need to be installed
import asyncio, discord, requests, dateparser, wikipedia, github3
wikipedia.set_lang("en")

try:
    cfg.GITHUBCHANNEL
    cfg.REPOS
except:
    pass
else:
    g = github3.GitHub()
    repos = []
    lastCommits = {}
    for r in range(len(cfg.REPOS)):
        repo = github3.repository(cfg.REPOS[r][0], cfg.REPOS[r][1])
        repos.append(repo)
        lastCommits[repo.id] = {}
        for b in repos[r].iter_branches():
            lastCommits[repo.id][b.name] = b.commit

#Client intialization stuff
client = discord.Client()

#Initialize help string
helpString = """PYBOT V5 HELP
http://github.com/MishaLarionov/pybot/tree/discord\n
Commands are called by preceeding them with `@pybot`, `-p`, or `!`
Examples: `@pybot help`, `-p help`, `!help`
`help` shows this page
`idea: <text>` Records a suggestion in your name. You can see it with @pybot getideas
`getideas <username>` Lists ideas from user. *username* can be omitted to get your own ideas.
`delidea <n>` Deletes the idea with the number *n*
`clearideas` Deletes ALL your ideas
`whatis <query>` Gets a summary of the Wikipedia page for <query>
`machineinfo` Gets server name and operating system
`splitchannel` Keeps future ideas from this channel separate from others, only accessible from the channel in which this command is run.
`mergechannel` Makes ideas from channel available to all channels.
`setresponse \"<response>\" for \"<call>\"` Has me respond with *response* whenever your message matches *call*
`getresponses` Gets all automated responses
`delresponse <call>` Deletes the response for call
`clearresponses` Deletes ALL responses
`getout` Makes pybot leave the server. Only usable by the owner.

To add me to your server visit http://bit.ly/getpybot
"""

print("Setup finished")

def readFile(channel):
    #Function for grabbing the dictionary from the file
    d = {"responses": {}}
    try:
        #See if the channel exists
        with open("data/" + channel.id + ".txt", 'r') as f:
            for line in f:
                #Grab the keys and values
                (key, val) = line.split("|", maxsplit = 1)
                #Rebuild the dictionary
                #Literally no clue how this line works
                d[key] = ast.literal_eval(val)
    except:
        try:
            #Open the main file if the channel is not separate
            with open("data/" + channel.server.id + ".txt", 'r') as f:
                for line in f:
                    #Grab the keys and values
                    (key, val) = line.split("|", maxsplit = 1)
                    #Rebuild the dictionary
                    #Literally no clue how this line works
                    d[key] = ast.literal_eval(val)
        except:
            try:
                #Create a new file if <server>.txt doesn't exist
                #Or if an error happens. (99% sure this is fixed)
                f = open("data/" + channel.server.id + ".txt", 'w')
                f.write("responses|{}")
            except:
                #Create a new file if the channel doesn't exist or belong to a server
                #Or if an error happens. (99% sure this is fixed)
                f = open("data/" + channel.id + ".txt", 'w')
                f.write("responses|{}")
    f.close()
    return(d)

def writeDict(d, channel):
    #Function to write the dictionary to the file
    s = ""
    #Get the keys to match them with index numbers
    keys = list(d.keys())
    for i in range(0, len(d)):
        #Write each line of the file with the proper syntax
        s = (s + keys[i] + "|" + str(d[keys[i]]) + "\n")
    try:
        f = open("data/" + channel.id + ".txt", 'w')
    except:
        f = open("data/" + channel.server.id + ".txt", 'w')
    #Overwrite the file with the new content
    f.write(s)
    f.close()
    return()

@asyncio.coroutine
def newIdea(text, user, channel):
    #Function to add idea for the user
    try:
        #Grab the dictionary from the file
        d = readFile(channel)
        #Create a backup in case something happens
        dProtect = readFile(channel)
        try:
            #Add the idea to the user's list of ideas
            d[user.id].append(text)
        except:
            #Create the user in the dictionary if they don't exist
            d[user.id] = [text]
        writeDict(d, channel)
        if readFile(channel) == {}:
            #Revert the file if an error wiped it
            yield from debug("Something wiped the file. Restoring to previous version...")
            writeDict(dProtect, channel)
    except Exception as e:
        yield from client.send_message(channel, ":warning: Sorry, I couldn't add your idea. Please try again!")
        writeDict(dProtect)
    else:
        yield from client.send_message(channel, "{}'s idea has been added.".format(user.mention))

@asyncio.coroutine
def getIdeas(name, channel):
    #Check if the user exists
    user = channel.server.get_member_named(name)
    if user:
        userID = user.id
        #Grab the dictionary from the text file
        d = readFile(channel)
        #Check if the user is in the idea dictionary
        if userID in d:
            #Check if the user has any ideas
            if len(d[userID]) > 0:
                #Output a numbered list of the user's ideas
                s = (":open_file_folder: Ideas for {}:".format(user.mention))
                for i in range(0, len(d[userID])):
                    s = (s + ("\n`" + str(i+1) + ":` " + d[userID][i]))
                yield from client.send_message(channel, s)
                #Begin descending staircase of error messages
            else:
                yield from client.send_message(channel, ":warning: " + user.mention + " has not entered any ideas yet!")
        else:
            yield from client.send_message(channel, ":warning: " + user.mention + " has not entered any ideas yet!")
    else:
        yield from client.send_message(channel, ":warning: Name not found! Please try again!")

@asyncio.coroutine
def delIdea(num, author, channel):
    try:
        #Makes sure "1" points to d[userID][0]
        num = int(num) - 1
        if num < 0:
            num = num + 1
        #Grab the dictionary from the text file
        d = readFile(channel)
        #Make sure the number is not greater than the amount of elements
        if (num + 1) > len(d[author]) and len(d[author]) > 0:
            client.send_message(channel, ":warning: That's more ideas than you have! You currently have " + str(len(d[author])) + " ideas entered.")
        elif len(d[author]) == 0:
            yield from client.send_message(channel, ":warning: You don't have any ideas to delete!")
        else:
            #Get rid of the element
            e = d[author].pop(num)
            #Rebuild the dictionary
            writeDict(d, channel)
            yield from client.send_message(channel, ":wastebasket: Idea `" + e.replace("`", "'") + "` deleted.")
    except:
        yield from client.send_message(channel, ":warning: Invalid number. Please try again.")

@asyncio.coroutine
def splitChannel(channel):
    #Overwrite the file with the new content
    try:
        f = open("data/" + channel.id + ".txt", 'r')
    except:
        f = open("data/" + channel.id + ".txt", 'w')
        f.write("responses|{}")
        yield from client.send_message(channel, "Any new ideas posted here will be kept separate and only accessible in this server.")
    else:
        yield from client.send_message(channel, "Channel already separate. Use `@pybot mergechannel` to merge this channel with the main branch, copying all data.")
    f.close()
    return()

@asyncio.coroutine
def mergeChannel(channel):
    #Overwrite the file with the new content
    try:
        f = open("data/" + channel.id + ".txt", 'r')
        f.close()
    except:
        yield from client.send_message(channel, "Channel uses the main idea database. Use `@pybot splitchannel` to split it.")
    else:
        try:
            server = channel.server.id
            d1 = readFile(channel)
            os.remove("data/" + channel.id + ".txt")
            d2 = readFile(channel)
            s = ""
            #Get the keys to match them with index numbers
            keys = list(d1.keys()) + list(d2.keys())
            
            for i in range(0, len(keys)):
                if keys[i] == "responses":
                    pass
                #Write each line of the file with the proper syntax
                elif keys[i] in d1:
                    if keys[i] in d2:
                        s = (s + keys[i] + "|" + str(d1[keys[i]] + d2[keys[i]]) + "\n")
                    else:
                        s = (s + keys[i] + "|" + str(d1[keys[i]]) + "\n")
                else:
                    s = (s + keys[i] + "|" + str(d2[keys[i]]) + "\n")
            s = (s + "responses|" + str(d2["responses"]))
            
            f2 = open("data/" + server + ".txt", 'w')
            f2.write(s)
            f2.close()
            yield from client.send_message(channel, "Successfully merged channel with the main branch.")
        except AttributeError:
            yield from client.send_message(channel, ":warning: This channel is not attached to a server, likely a Direct Message. Ideas cannot be merged.")
    return()

@asyncio.coroutine
def clearIdeas(author, channel):
    #Grab the dictionary from the text file
    d = readFile(channel)
    if (not author.id in d.keys()) or len(d[author.id]) == 0:
        yield from client.send_message(channel, ":warning: You don't have any ideas to delete!")
    else:
        d[author.id] = []
        writeDict(d, channel)
        yield from client.send_message(channel, ":wastebasket: Ideas for {} cleared.".format(author.mention))
    

def setReminder():
    #Unfinished reminder code
    event = message.content.split(" ", maxsplit = 1)[1]
    (name, datetime) = event.split("@", maxsplit = 1)
    name = name.strip()
    dtime = dateparser.parse(datetime)
    s = sched.scheduler()
    s.enterabs(dtime.timestamp(), 1, (remind, message.channel), name)
    s.run()

@asyncio.coroutine
def setResponse(response, call, channel):
    d = readFile(channel)
    #No idea what this regex does, Nicholas needs to comment this
    call = re.sub('([.,!?()])', r' \1 ', call)
    if call in d["responses"]:
        oldresponse = d["responses"][call]
        d["responses"][call] = response
        writeDict(d, channel)
        yield from client.send_message(channel, "Changed response from `" + oldresponse + "` to `" + response + "`.")
    else:
        d["responses"][call] = response
        writeDict(d, channel)
        yield from client.send_message(channel, "Added response to list")

@asyncio.coroutine
def whatIs(user, channel, message):
    searchResults = wikipedia.search(message)
    if len(searchResults) < 1:
        yield from client.send_message(channel, ":warning: Could not find anything matching your search, {}. Try using different keywords.".format(user.mention))
    else:
        try:
            page = wikipedia.page(searchResults[0], auto_suggest = True, redirect = True)
            output = '{}, here you go:\n**'.format(user.mention) + page.title + "**\nFrom <" + page.url + ">\n" + wikipedia.summary(searchResults[0], sentences=1)
            yield from client.send_message(channel, output)
        except wikipedia.exceptions.DisambiguationError as e:
            yield from client.send_message(channel, '{}, '.format(user.mention) + str(e))
            

@asyncio.coroutine
def delResponse(call, channel):
    d = readFile(channel)
    #No idea what this regex does, Nicholas needs to comment this
    call = re.sub('([.,!?()])', r' \1 ', call)
    if call in d["responses"]:
        del(d["responses"][call])
        writeDict(d, channel)
        yield from client.send_message(channel, ":wastebasket: Removed response.")
    else:
        yield from client.send_message(channel, ":warning: I don't respond to that!")

@asyncio.coroutine
def getResponses(channel):
    d = readFile(channel)
    #Check if there are any responses
    if d["responses"]:
        #Output a numbered list of the user's ideas
        s = ("I respond with:")
        for i in d["responses"]:
            s = (s + ("\n`" + d["responses"][i] + "` for `" + i + "`"))
        yield from client.send_message(channel, s)
    else:
        yield from client.send_message(channel, ":warning: There are no responses here!")

@asyncio.coroutine
def clearResponses(channel):
    d = readFile(channel)
    #Make sure there are responses to clear
    if len(d["responses"]) > 0:
        #Bushwhack all the responses
        d["responses"] = {}
        writeDict(d, channel)
        yield from client.send_message(channel, ":wastebasket: Removed responses.")
    else:
        yield from client.send_message(channel, ":warning: There are no responses here!")

@asyncio.coroutine
def versionInfo(channel):
    #Basically looks at itself and compares itself with the github
    sourcetemp = open("bot.py", "r")
    #Look at own code
    currentcode = sourcetemp.read()
    #Load code from GitHub for stable and unstable branches
    stablecode = requests.get('https://raw.githubusercontent.com/MishaLarionov/pybot/discord/bot.py')
    unstablecode = requests.get('https://raw.githubusercontent.com/MishaLarionov/pybot/discord-unstable/bot.py')
    #Compare both code samples
    if currentcode == stablecode.text:
        yield from client.send_message(channel, ":thumbsup: This bot instance is up to date with the latest stable build.")
    elif currentcode == unstablecode.text:
        yield from client.send_message(channel, ":alembic: This bot instance is up to date with the latest unstable build.")
    else:
        yield from client.send_message(channel, ":warning: This bot instance does not match any known version. Please bother Misha Larionov (@Marsroverr) or Nicholas Carr (@ncarr).")

@asyncio.coroutine
def getChanges(repos, lastCommits):
    while True:
        #Make sure we have the freshest data, but tell the server to give us nothing if our data is already fresh
        for repo in repos:
            repo.refresh(conditional=True)
            for b in repo.iter_branches():
                #If anything actually happened
                if b.commit != lastCommits[repo.id][b.name]:
                    events = repo.iter_events()
                    #Go through everything that ever happened on the repo to see what's new
                    for i in events:
                        #If we pushed some changes and the old commit came in just before this change
                        if i.type == "PushEvent" and i.payload["before"] == lastCommits[repo.id][b.name].sha:
                            #Draft the beginning of the message
                            m = "[" + repo.name + "] " + str(i.payload["size"]) + " new commit" + ("s" if i.payload["size"] != 1 else "") + " pushed by " + i.actor.login + " <" + repo.compare_commits(i.payload["before"], i.payload["head"]).html_url + ">:\n"
                            for c in i.payload["commits"]:
                                #Describe each new commit
                                m += "`" + c["sha"][:7] + "` " + c["message"] + " - " + c["author"]["name"] + " - <" + repo.commit(c["sha"]).html_url + ">\n"
                            yield from client.send_message(client.get_channel(cfg.GITHUBCHANNEL), m)
                            #Update the last seen commit for later
                            lastCommits[repo.id][b.name] = repo.commit(i.payload["head"])
                            #If this is the last event which occured between updates
                            if i.payload["head"] == repo.commit("discord-unstable").sha:
                                break
        yield from asyncio.sleep(120)

@asyncio.coroutine
def processCommand(rawstring, channel, user, message):
    #Process the user's commands
    if " " in rawstring:
        (cmd, message) = rawstring.split(" ", maxsplit = 1)
        cmd = cmd.lower()
        if cmd == "hello":
            yield from client.send_message(channel, 'Hello, {}!'.format(user.mention))
        elif cmd == "idea" or cmd == "idea:":
            yield from newIdea(message, user, channel)
        elif cmd == "getideas":
            yield from getIdeas(message, channel)
        elif cmd == "delidea":
            yield from delIdea(message, user.id, channel)
        elif cmd == "clearideas":
            yield from clearIdeas(user, channel)
        elif cmd == "whatis":
            yield from whatIs(user, channel, message)
        elif cmd == "what":
            if message.startswith("is "):
                yield from whatIs(user, channel, message[3:])
            elif message.startswith("are "):
                yield from whatIs(user, channel, message[4:])
            elif message.startswith("was "):
                yield from whatIs(user, channel, message[4:])
            elif message.startswith("were "):
                yield from whatIs(user, channel, message[5:])
            else:
                yield from client.send_message(channel, ":warning: Unknown command. `@pybot help` for a list of commands.")
        elif cmd == "remind":
            #Code goes here someday
            print("Reminder code doesn't exist yet, please create some.")
            yield from client.send_message(channel, ":warning: Nicholas (@ncarr) forgot to write this code.")
        elif cmd == "help":
            yield from client.send_message(channel, helpString)
        elif cmd == "setresponse":
            try:
                yield from setResponse(message.split("\"")[1], message.split("\"")[3], channel)
            except IndexError:
                try:
                    yield from setResponse(message.split("'")[1], message.split("'")[3], channel)
                except IndexError:
                    yield from client.send_message(channel, ":warning: Improper syntax! Please use either single or double quotes for both call and response!")
        elif cmd == "delresponse":
            yield from delResponse(message, channel)
        else:
            yield from client.send_message(channel, ":warning: Unknown command. `@pybot help` for a list of commands.")
    else:
        rawstring = rawstring.lower()
        if rawstring == "hello":
            yield from client.send_message(channel, 'Hello, {}!'.format(user.mention))
        elif rawstring == "die" or rawstring == "kys":
            print(user.name + " tried to kill the bot!")
            #Find the people that are allowed to kill the bot
            if user.id in cfg.KILLERIDS:
                yield from client.send_message(channel, ":robot::gun:")
                time.sleep(1)
                yield from client.send_message(channel, ":boom::gun:")
                print(user.name + " has killed me! Avenge me!") 
                sys.exit()
            else:
                yield from client.send_message(channel, ":warning: You don't have permission to kill me! I see you don't like me, perhaps you don't understand my commands. `@pybot help` to learn more. If you really hate me, get your channel owner to send `@pybot getout`.")
        elif rawstring == "clearideas":
            yield from clearIdeas(user, channel)
        elif rawstring == "machineinfo":
            yield from client.send_message(channel, platform.node() + " " + platform.platform())
        elif rawstring == "help":
            yield from client.send_message(user, helpString)
            yield from client.delete_message(message)
        elif rawstring == "getideas":
            yield from getIdeas(user.name, channel)
        elif rawstring == "getresponses":
            yield from getResponses(channel)
        elif rawstring == "clearresponses":
            yield from clearResponses(channel)
        elif rawstring == "splitchannel":
            yield from splitChannel(channel)
        elif rawstring == "mergechannel":
            yield from mergeChannel(channel)
        elif rawstring == "versioninfo":
            yield from versionInfo(channel)
        elif rawstring == "getout":
            if user == channel.server.owner:
                yield from client.send_message(channel, "Alright, I'll leave your server.. :cry:\n(http://bit.ly/getpybot to re-add me)")
                yield from client.leave_server(channel.server)
            else:
                yield from client.send_message(channel, ":warning: Only the server owner can make me leave!")
        else:
            yield from client.send_message(channel, ":warning: Unknown command. `@pybot help` for proper commands.")

@asyncio.coroutine
def remind(name, channel):
    #Unfinished useless code
    yield from client.send_message(channel, "You asked me to remind you to" + name)

@asyncio.coroutine
def debug(text):
    #Automatically decides whether to debug or not
    if cfg.DEBUGMODE:
        debug = client.get_channel(cfg.DEBUGCH)
        yield from client.send_message(debug, text)

@asyncio.coroutine
def processResponse(message):
    for word in readFile(message.channel)["responses"]:
        #Pad and sub to ensure only whole words are matched and punctuation doesn't stop matches
        if (" " + word + " ") in re.sub('([.,!?()])', r' \1 ', " " + message.content + " "):
            yield from client.send_message(message.channel, readFile(message.channel)["responses"][word])
            return True
    return False

@client.event
@asyncio.coroutine
def on_message(message):
    print(time.strftime("%Y-%m-%d %H:%M:%S") + ": " + message.author.name + " says: " + message.content)
    if message.author == client.user:
        return
    #Uncomment this if you want to use an exclamaion mark instead of @pybot
    if message.content.startswith("!") and len(message.content) > 1:
        yield from processCommand(message.content[1:], message.channel, message.author, message)
    if message.content.startswith("<@" + client.user.id + ">") and len(message.content) > 22:
        yield from client.send_typing(message.channel)
        yield from processCommand(str.strip(message.content[22:]), message.channel, message.author, message)
    if message.content.startswith("@" + client.user.name) and len(message.content) > 7:
        yield from client.send_typing(message.channel)
        yield from processCommand(str.strip(message.content[7:]), message.channel, message.author, message)
    elif message.content.startswith("-p"):
        yield from client.send_typing(message.channel)
        yield from processCommand(str.strip(message.content[3:]), message.channel, message.author, message)
    elif message.content == "<@" + client.user.id + ">" or message.content == "-p" or message.content == "@" + client.user.name:
        yield from client.send_message(message.channel, 'Hello {}!'.format(message.author.mention))
    elif message.content == "sudo rm -rf":
        yield from processCommand("clearideas", message.channel, message.author, message)
    else:
        yield from processResponse(message)
@client.event
@asyncio.coroutine
def on_ready():
    print(time.strftime("%Y-%m-%d %H:%M:%S") + ': Connected to Discord')
    try:
        cfg.GITHUBCHANNEL
        cfg.REPOS
    except:
        pass
    else:
        yield from getChanges(repos, lastCommits)

client.run(cfg.TOKEN)
