#Pybot discord-unstable build
#Misha Larionov and Nicholas Carr
#github.com/MishaLarionov/pybot/tree/discord-unstable

#TODO:
#Support multiple servers from one bot instance (Basically more .txt files)
#Add todo command (Literally just a clone/rename of ideas)

print("Loading... (This may take a while)")

#Import all the stuff
import cfg, time, platform, ast, sys, os, re
#Second line of import statements. These may need to be installed
import asyncio, discord, requests, dateparser

#Client intialization stuff
client = discord.Client()

#Initialize help string
helpstring = """PYBOT V5 HELP
http://github.com/MishaLarionov/pybot/tree/discord\n
`@pybot help` shows this page
`@pybot idea: <text>` Records a suggestion in your name. You can see it with @pybot getideas
`@pybot getideas <username>` lists ideas from user. *username* can be omitted to get your own ideas.
`@pybot delidea <n>` deletes the idea with the number *n*
`@pybot clearideas` deletes ALL your ideas
`@pybot machineinfo` Gets server name and operating system
`@pybot splitchannel` Keeps future ideas from this channel separate from others, only accessible from the channel in which this command is run.
`@pybot mergechannel` Makes ideas from channel available to all channels.
`@pybot setresponse \"<response>\" for \"<call>\"` Has me respond with *response* whenever your message matches *call*
`@pybot getresponses` Gets all automated responses
`@pybot delresponse <call>` Deletes the response for call
`@pybot clearresponses` Deletes ALL responses
"""

def readfile(channel):
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
                #Or if an error happens. Possibly fixed.
                f = open("data/" + channel.server.id + ".txt", 'w')
                f.write("responses|{}")
            except:
                #Create a new file if the channel doesn't exist or belong to a server
                #Or if an error happens. Possibly fixed.
                f = open("data/" + channel.id + ".txt", 'w')
                f.write("responses|{}")
    f.close()
    return(d)

def writedict(d, channel):
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
def newidea(text, user, channel):
    #Function to add idea for the user
    try:
        #Grab the dictionary from the file
        d = readfile(channel)
        #Create a backup in case something happens
        dprotect = readfile(channel)
        try:
            #Add the idea to the user's list of ideas
            d[user.id].append(text)
        except:
            #Create the user in the dictionary if they don't exist
            d[user.id] = [text]
        writedict(d, channel)
        if readfile(channel) == {}:
            yield from debug("Something wiped the file. Restoring to previous version...")
            writedict(dprotect, channel)
    except Exception as e:
        yield from client.send_message(channel, "Sorry, I couldn't add your idea. Please try again!")
        writedict(dprotect)
    else:
        yield from client.send_message(channel, "{}'s idea has been added.".format(user.mention))

@asyncio.coroutine
def getideas(name, channel):
    mentions = []
    userNames = []
    userIDs = []
    #This is insecure and needs to be changed
    try:
        for member in channel.server.members:
            mentions.append(member.mention)
            userNames.append(member.name.lower())
            userIDs.append(member.id)
    except AttributeError:
        mentions.append(channel.user.mention)
        userNames.append(channel.user.name.lower())
        userIDs.append(channel.user.id)
    #Check if the user exists
    if name.lower() in userNames:
        #Put all this in a function eventually maybe?
        userpos = userNames.index(name.lower())
        userID = userIDs[userpos]
        #Grab the dictionary from the text file
        d = readfile(channel)
        #Check if the user is in the idea dictionary
        if userID in d:
            #Check if the user has any ideas
            if len(d[userID]) > 0:
                #Output a numbered list of the user's ideas
                s = ("Ideas for " + mentions[userpos] + ":")
                for i in range(0, len(d[userID])):
                    s = (s + ("\n`" + str(i+1) + ":` " + d[userID][i]))
                yield from client.send_message(channel, s)
                #Begin descending staircase of error messages
            else:
                yield from client.send_message(channel, mentions[userpos] + " has not entered any ideas yet!")
        else:
            yield from client.send_message(channel, mentions[userpos] + " has not entered any ideas yet!")
    else:
        yield from client.send_message(channel, "Name not found! Please try again!")

@asyncio.coroutine
def delidea(num, author, channel):
    try:
        #Makes sure "1" points to d[userID][0]
        num = int(num) - 1
        if num < 0:
            num = num + 1
        #Grab the dictionary from the text file
        d = readfile(channel)
        #Make sure the number is not greater than the amount of elements
        if (num + 1) > len(d[author]) and len(d[author]) > 0:
            client.send_message(channel, "That's more ideas than you have! You currently have " + str(len(d[author])) + " ideas entered.")
        elif len(d[author]) == 0:
            yield from client.send_message(channel, "You don't have any ideas to delete!")
        else:
            #Get rid of the element
            e = d[author].pop(num)
            #Rebuild the dictionary
            writedict(d, channel)
            yield from client.send_message(channel, "Idea `" + e.replace("`", "'") + "` deleted.")
    except:
        yield from client.send_message(channel, "Invalid number. Please try again.")

@asyncio.coroutine
def splitchannel(channel):
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
def mergechannel(channel):
    #Overwrite the file with the new content
    try:
        f = open("data/" + channel.id + ".txt", 'r')
        f.close()
    except:
        yield from client.send_message(channel, "Channel uses the main idea database. Use `@pybot splitchannel` to split it.")
    else:
        try:
            server = channel.server.id
            d1 = readfile(channel)
            os.remove("data/" + channel.id + ".txt")
            d2 = readfile(channel)
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
            yield from client.send_message(channel, "This channel is not attached to a server, likely a Direct Message. Ideas cannot be merged.")
    return()

@asyncio.coroutine
def clearideas(author, channel):
    #Grab the dictionary from the text file
    d = readfile(channel)
    if len(d[author.id]) == 0:
        yield from client.send_message(channel, "You don't have any ideas to delete!")
    else:
        d[author.id] = []
        writedict(d, channel)
        yield from client.send_message(channel, "Ideas for {} cleared.".format(author.mention))
    

def setreminder():
    #Nicholas's uncommented reminder code
    #I don't even think this function is ever called
    #Nicholas why is this here
    #I'll just keep adding comments every update until you fix this
    #Nicholas, what is this function doing in my code
    #Aaaand he still hasn't fixed it.
    event = message.content.split(" ", maxsplit = 1)[1]
    (name, datetime) = event.split("@", maxsplit = 1)
    name = name.strip()
    dtime = dateparser.parse(datetime)
    s = sched.scheduler()
    s.enterabs(dtime.timestamp(), 1, (remind, message.channel), name)
    s.run()

@asyncio.coroutine
def setresponse(response, call, channel):
    d = readfile(channel)
    call = re.sub('([.,!?()])', r' \1 ', call)
    if call in d["responses"]:
        oldresponse = d["responses"][call]
        d["responses"][call] = response
        writedict(d, channel)
        yield from client.send_message(channel, "Changed response from `" + oldresponse + "` to `" + response + "`.")
    else:
        d["responses"][call] = response
        writedict(d, channel)
        yield from client.send_message(channel, "Added response to list")

@asyncio.coroutine
def delresponse(call, channel):
    d = readfile(channel)
    call = re.sub('([.,!?()])', r' \1 ', call)
    if call in d["responses"]:
        del(d["responses"][call])
        writedict(d, channel)
        yield from client.send_message(channel, "Removed response.")
    else:
        yield from client.send_message(channel, "I don't respond to that!")

@asyncio.coroutine
def getresponses(channel):
    d = readfile(channel)
    #Check if there are any responses
    if d["responses"]:
        #Output a numbered list of the user's ideas
        s = ("I respond with:")
        for i in d["responses"]:
            s = (s + ("\n`" + d["responses"][i] + "` for `" + i + "`"))
        yield from client.send_message(channel, s)
    else:
        yield from client.send_message(channel, "There are no responses here!")

@asyncio.coroutine
def clearresponses(channel):
    d = readfile(channel)
    if len(d["responses"]) > 0:
        d["responses"] = {}
        writedict(d, channel)
        yield from client.send_message(channel, "Removed responses.")
    else:
        yield from client.send_message(channel, "There are no responses here!")

@asyncio.coroutine
def versioninfo(channel):
    #This might work. Probably.
    sourcetemp = open("bot.py", "r")
    currentcode = sourcetemp.read()
    stablecode = requests.get('https://raw.githubusercontent.com/MishaLarionov/pybot/discord/bot.py')
    unstablecode = requests.get('https://raw.githubusercontent.com/MishaLarionov/pybot/discord-unstable/bot.py')
    if currentcode == stablecode.text:
        yield from client.send_message(channel, "This bot instance is up to date with the latest stable build.")
    elif currentcode == unstablecode.text:
        yield from client.send_message(channel, "This bot instance is up to date with the latest unstable build.")
    else:
        yield from client.send_message(channel, "This bot instance does not match any known version. Please bother Misha Larionov (@Marsroverr) or Nicholas Carr (@ncarr).")
    
    
@asyncio.coroutine
def processcommand(rawstring, channel, user):
    #Process the user's commands
    if " " in rawstring:
        (cmd, message) = rawstring.split(" ", maxsplit = 1)
        cmd = cmd.lower()
        if cmd == "hello":
            yield from client.send_message(channel, 'Hello, {}!'.format(user.mention))
        elif cmd == "idea" or cmd == "idea:":
            yield from newidea(message, user, channel)
        elif cmd == "getideas":
            yield from getideas(message, channel)
        elif cmd == "delidea":
            yield from delidea(message, user.id, channel)
        elif cmd == "clearideas":
            yield from clearideas(user, channel)
        elif cmd == "remind":
            #Code goes here someday
            print("Reminder code doesn't exist yet, please create some.")
            yield from client.send_message(channel, "Remind command has not been migrated to new format.")
        elif cmd == "help":
            yield from client.send_message(channel, helpstring)
        elif cmd == "setresponse":
            try:
                yield from setresponse(message.split("\"")[1], message.split("\"")[3], channel)
            except IndexError:
                yield from client.send_message(channel, "Improper syntax! For me to understand responses with spaces, please put your call and response in double quotes.")
        elif cmd == "delresponse":
            yield from delresponse(message, channel)
        else:
            yield from client.send_message(channel, "Unknown command. Please try again.")
    else:
        rawstring = rawstring.lower()
        if rawstring == "hello":
            yield from client.send_message(channel, 'Hello, {}!'.format(user.mention))
        if rawstring == "die":
            try:
                if any(cfg.ADMINROLE == role.id for role in user.roles):
                    #Kill the bot with the top-secret kill switch
                    yield from client.send_message(channel, "brb dying")
                    print(user.name + " has killed me! Avenge me!") 
                    yield from client.logout()
            except:
                yield from client.send_message(channel, "You need to be in a server to kill me.")
        elif rawstring == "clearideas":
            yield from clearideas(user, channel)
        elif rawstring == "machineinfo":
            yield from client.send_message(channel, platform.node() + " " + platform.platform())
        elif rawstring == "help":
            yield from client.send_message(channel, helpstring)
        elif rawstring == "getideas":
            yield from getideas(user.name, channel)
        elif rawstring == "getresponses":
            yield from getresponses(channel)
        elif rawstring == "clearresponses":
            yield from clearresponses(channel)
        elif rawstring == "splitchannel":
            yield from splitchannel(channel)
        elif rawstring == "mergechannel":
            yield from mergechannel(channel)
        elif rawstring == "versioninfo":
            yield from versioninfo(channel)
            #pass
        else:
            yield from client.send_message(channel, "Unknown command. Please try again.")

@asyncio.coroutine
def remind(name, channel):
    yield from client.send_message(channel, "You asked me to remind you to" + name)

@asyncio.coroutine
def debug(text):
    #Automatically decides whether to debug or not
    if cfg.DEBUGMODE:
        debug = client.get_channel(cfg.DEBUGCH)
        yield from client.send_message(debug, text)

@asyncio.coroutine
def processresponse(message):
    for word in readfile(message.channel)["responses"]:
        #Pad and sub to ensure only whole words are matched and punctuation doesn't stop matches
        if (" " + word + " ") in re.sub('([.,!?()])', r' \1 ', " " + message.content + " "):
            yield from client.send_message(message.channel, readfile(message.channel)["responses"][word])
            return True
    return False

@client.event
@asyncio.coroutine
def on_message(message):
    print(time.strftime("%Y-%m-%d %H:%M:%S") + ": " + message.author.name + " says: " + message.content)
    if message.author == client.user:
        return
    #if message.content.startswith("!") and len(message.content) > 1:
        #yield from processcommand(message.content[1:], message.channel, message.author)
    if message.content.startswith("<@" + client.user.id + ">") and len(message.content) > 22:
        yield from processcommand(str.strip(message.content[22:]), message.channel, message.author)
    if message.content.startswith("@" + client.user.name) and len(message.content) > 7:
        yield from processcommand(str.strip(message.content[7:]), message.channel, message.author)
    elif message.content == "<@" + client.user.id + ">":
        yield from client.send_message(message.channel, 'Hello {}!'.format(message.author.mention))
    elif message.content == "@" + client.user.name:
        yield from client.send_message(message.channel, 'Hello {}!'.format(message.author.mention))
    else:
        yield from processresponse(message)
@client.event
@asyncio.coroutine
def on_ready():
    print(time.strftime("%Y-%m-%d %H:%M:%S") + ': Connected to Discord')

client.run(cfg.TOKEN)
