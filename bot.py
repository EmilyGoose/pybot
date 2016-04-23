#Pybot discord-unstable build
#Misha Larionov and Nicholas Carr
#github.com/MishaLarionov/pybot/tree/discord-unstable

#TODO:
#Support multiple servers from one bot instance (Basically more .txt files)
#Add todo command (Literally just a clone/rename of ideas)

print("Loading... (This may take a while)")

#Import all the stuff, probably
import discord, cfg, time, platform, ast, sched, sys, os, dateparser

#Client intialization stuff
client = discord.Client()
client.login(cfg.EMAIL, cfg.PASSWORD)

#Initialize help string
helpstring = """PYBOT V5 HELP
http://github.com/MishaLarionov/pybot/tree/discord\n
`@pybot help` shows this page
`@pybot idea: <text>` Records a suggestion in your name. You can see it with @pybot getideas
`@pybot getideas <username>` lists ideas from user. *username* can be omitted to get your own ideas.
`@pybot delidea <n>` deletes the idea with the number *n*
`@pybot clearideas` deletes ALL your ideas
`@pybot machineinfo` Returns server name and operating system
`@pybot splitchannel` Keeps future ideas from this channel separate from others, only accessible from the channel in which this command is run. Can be undone with `@pybot mergechannel`
`@pybot mergechannel` Makes ideas from channel available to all channels; undoes `@pybot splitchannel`.
`@pybot setresponse \"<response>\" for \"<call>\"` Has me respond whenever your message matches *call*
"""

def readfile(channel):
    #Function for grabbing the dictionary from the file
    d = {}
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
            with open("data/dict.txt", 'r') as f:
                for line in f:
                    #Grab the keys and values
                    (key, val) = line.split("|", maxsplit = 1)
                    #Rebuild the dictionary
                    #Literally no clue how this line works
                    d[key] = ast.literal_eval(val)
        except:
            #Create a new file if dict.txt doesn't exist
            #Or if an error happens. Possibly fixed.
            f = open("data/dict.txt", 'w')
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
        f = open("data/dict.txt", 'w')
    #Overwrite the file with the new content
    f.write(s)
    f.close()
    return()

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
            debug("Something wiped the file. Restoring to previous version...")
            writedict(dprotect, channel)
    except Exception as e:
        client.send_message(channel, "Sorry, I couldn't add your idea. Please try again!")
        writedict(dprotect)
    else:
        client.send_message(channel, "{}'s idea has been added.".format(user.mention()))

def getideas(name, channel):
    userNames = []
    userIDs = []
    #This is insecure and needs to be changed
    for server in client.servers:
        for member in server.members:
            userNames.append(member.name.lower())
            userIDs.append(member.id)
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
                s = ("Ideas for " + name.title() + ":")
                for i in range(0, len(d[userID])):
                    s = (s + ("\n`" + str(i+1) + ":` " + d[userID][i]))
                client.send_message(channel, s)
                #Begin descending staircase of error messages
            else:
                client.send_message(channel, name.title() + " has not entered any ideas yet!")
        else:
            client.send_message(channel, name.title() + " has not entered any ideas yet!")
    else:
        client.send_message(channel, "Name not found! Please try again!")

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
            client.send_message(channel, "You don't have any ideas to delete!")
        else:
            #Get rid of the element
            e = d[author].pop(num)
            #Rebuild the dictionary
            writedict(d, channel)
            client.send_message(channel, "Idea `" + e.replace("`", "'") + "` deleted.")
    except:
        client.send_message(channel, "Invalid number. Please try again.")
def splitchannel(channel):
    #Overwrite the file with the new content
    try:
        f = open(channel.id + ".txt", 'r')
    except:
        f = open(channel.id + ".txt", 'w')
        f.write("responses|{}")
        client.send_message(channel, "Any new ideas posted here will be kept separate and only accessible in this channel.")
    else:
        client.send_message(channel, "Channel already separate. Use `@pybot mergechannel` to merge this channel with the main idea database, copying all data.")
    f.close()
    return()

def mergechannel(channel):
    #Overwrite the file with the new content
    try:
        f = open(channel.id + ".txt", 'r')
        f.close()
    except:
        client.send_message(channel, "Channel uses the main idea database. Use `@pybot splitchannel` to split it.")
    else:
        d1 = readfile(channel)
        os.remove(channel.id + ".txt")
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
        
        f2 = open("dict.txt", 'w')
        f2.write(s)
        f2.close()
        client.send_message(channel, "Successfully merged channel.")
    return()

def clearideas(author, channel):
    #Grab the dictionary from the text file
    d = readfile(channel)
    if len(d[author.id]) == 0:
        client.send_message(channel, "You don't have any ideas to delete!")
    else:
        d[author.id] = []
        writedict(d, channel)
        client.send_message(channel, "Ideas for {} cleared.".format(author.mention()))
    

def setreminder():
    #Nicholas's uncommented reminder code
    #I don't even think this function is ever called
    event = message.content.split(" ", maxsplit = 1)[1]
    (name, datetime) = event.split("@", maxsplit = 1)
    name = name.strip()
    dtime = dateparser.parse(datetime)
    s = sched.scheduler()
    s.enterabs(dtime.timestamp(), 1, (remind, message.channel), name)
    s.run()

def setresponse(response, call, channel):
    d = readfile(channel)
    if call in d["responses"]:
        client.send_message(channel, "I already respond with `" + d[call] + "`")
    else:
        d["responses"][call] = response
        writedict(d, channel)
        client.send_message(channel, "Added response to list")

def processcommand(rawstring, channel, user):
    #Process the user's commands
    if " " in rawstring:
        (cmd, message) = rawstring.split(" ", maxsplit = 1)
        if cmd == "hello":
            client.send_message(channel, 'Hello, {}!'.format(user.mention()))
        elif cmd == "idea" or cmd == "idea:":
            newidea(message, user, channel)
        elif cmd == "getideas":
            getideas(message, channel)
        elif cmd == "delidea":
            delidea(message, user.id, channel)
        elif cmd == "clearideas":
            clearideas(user, channel)
        elif cmd == "remind":
            #Code goes here someday
            print("Reminder code doesn't exist yet, please create some.")
            client.send_message(channel, "Remind command has not been migrated to new format.")
        elif cmd == "help":
            client.send_message(channel, helpstring)
        elif cmd == "setresponse":
            setresponse(message.split("\"")[1], message.split("\"")[3], channel)
        else:
            client.send_message(channel, "Unknown command. Please try again.")
    else:
        if rawstring == "hello":
            client.send_message(channel, 'Hello, {}!'.format(user.mention()))
        if rawstring == "die" and user.name in ["ncarr", "Marsroverr"]:
            #Kill the bot with the top-secret kill switch
            client.send_message(channel, "brb dying")
            print(user.name + " has killed me! Avenge me!") 
            sys.exit()
        elif rawstring == "clearideas":
            clearideas(user, channel)
        elif rawstring == "machineinfo":
            client.send_message(channel, platform.node() + " " + platform.platform())
        elif rawstring == "help":
            client.send_message(channel, helpstring)
        elif rawstring == "getideas":
            getideas(user.name, channel)
        elif rawstring == "splitchannel":
            splitchannel(channel)
        elif rawstring == "mergechannel":
            mergechannel(channel)
        else:
            client.send_message(channel, "Unknown command. Please try again.")

def remind(name, channel):
    client.send_message(channel, "You asked me to remind you to" + name)

def debug(text):
    #Automatically decides whether to debug or not
    if cfg.DEBUGMODE:
        debug = client.get_channel(cfg.DEBUGCH)
        client.send_message(debug, text)

@client.event
def on_message(message):
    print(time.strftime("%Y-%m-%d %H:%M:%S") + ": " + message.author.name.title() + " says: " + message.content)    
    if message.author == client.user:
        return
    #if message.content.startswith("!") and len(message.content) > 1:
        #processcommand(message.content[1:], message.channel, message.author)
    if message.content.startswith("<@" + cfg.BOTID + ">") and len(message.content) > 22:
        processcommand(str.strip(message.content[22:]), message.channel, message.author)
    if message.content.startswith("@" + cfg.BOTNAME) and len(message.content) > 7:
        processcommand(str.strip(message.content[7:]), message.channel, message.author)
    elif message.content == "<@" + cfg.BOTID + ">":
        client.send_message(message.channel, 'Hello {}!'.format(message.author.mention()))
    elif message.content in readfile(message.channel)["responses"]:
        client.send_message(message.channel, readfile(message.channel)["responses"][message.content])

@client.event
def on_ready():
    print(time.strftime("%Y-%m-%d %H:%M:%S") + ': Connected to Discord')

client.run()
createLists()
