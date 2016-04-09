#Pybot discord-unstable build
#Misha Larionov and Nicholas Carr
#github.com/MishaLarionov/pybot/tree/discord-unstable

#TODO:
#Rework command system
#Support multiple servers from one bot instance
#Add todo command

import discord, cfg, time, platform, ast, sched, sys
#import dateparser

#Client intialization stuff
client = discord.Client()
client.login(cfg.EMAIL, cfg.PASSWORD)
if cfg.DEBUGMODE:
    debug = client.get_channel(cfg.DEBUGCH)

def readfile():
    d = {}
    try:
        #Open the file
        with open("dict.txt", 'r') as f:
            for line in f:
                #Grab the keys and values
                (key, val) = line.split("|", maxsplit = 1)
                #Rebuild the dictionary
                #Literally no clue how this line works
                d[key] = ast.literal_eval(val)
    except:
        #Create a new file if dict.txt doesn't exist
        #Or if an error happens. I'll fix that later.
        f = open("dict.txt", 'w')
    f.close()
    return(d)

def writedict(d):
    s = ""
    #Get the keys to match them with index numbers
    keys = list(d.keys())
    for i in range(0, len(d)):
        #Write each line of the file with the proper syntax
        s = (s + keys[i] + "|" + str(d[keys[i]]) + "\n")
    f = open("dict.txt", 'w')
    #Overwrite the file with the new content
    f.write(s)
    f.close()
    return()

def newidea(name, text):
    debug = client.get_channel(cfg.DEBUGCH)
    try:
        #Grab the dictionary from the file
        dprotect = readfile()
        d = readfile()
        try:
            #Add the idea to the user's list of ideas
            d[name].append(text)
        except:
            #Create the user in the dictionary if they don't exist
            d[name] = [text]
        writedict(d)
        if readfile() == {}:
            client.send_message(debug, "Something wiped the file. Restoring to previous version...")
            writedict(dprotect)
        return()       
    except Exception as e:
        client.send_message(message.channel, "Sorry, I couldn't add your idea. Please try again!")
        writedict(dprotect)
    else:
        client.send_message(message.channel, "{}'s idea has been added.".format(message.author.mention()))

def getideas(name, channel):
    #message is not defined FIX
    userNames = []
    userIDs = []
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
        d = readfile()
        #Check if the user is in the idea dictionary
        if userID in d:
            #Check if the user has any ideas
            if len(d[userID]) > 0:
                #Output a numbered list of the user's ideas
                s = ("Ideas for " + name.title() + ":")
                for i in range(0, len(d[userID])):
                    s = (s + ("\n" + str(i+1) + ": " + d[userID][i]))
                client.send_message(channel, s)
            else:
                client.send_message(channel, name.title() + " has not entered any ideas yet!")
        else:
            client.send_message(channel, name.title() + " has not entered any ideas yet!")
    else:
        client.send_message(channel, "Name not found! Please try again!")

def processcommand(rawstring, channel, user):
    #This function doesn't do anything yet but it will eventually
    (cmd, message) = rawstring.split(" ", maxsplit = 1)
    if cmd == "hello":
        client.send_message(channel, 'Hello {}!'.format(user.mention()))
    elif cmd == "idea":
        newidea(user.id, message)
    elif cmd == "getideas":
        getideas(message, channel)
        pass
    elif cmd == "delidea":
        #Code goes here someday
        pass
    elif cmd == "remind":
        #Code goes here someday
        pass
    elif cmd == "help":
        #Code goes here someday
        pass
    elif cmd == "die":
        #Secure killswitch
        pass

def remind(name, channel):
    client.send_message(channel, "You asked me to remind you to" + name)

@client.event
def on_message(message):
    debug = client.get_channel(cfg.DEBUGCH)
    print(time.strftime("%Y-%m-%d %H:%M:%S") + ": " + message.author.name.title() + " says: " + message.content)
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        client.send_message(message.channel, 'Hello {}!'.format(message.author.mention()))
    #Handle new ideas
    if message.content.startswith('!idea:'):
        newidea(message.author.id, message.content.split(": ", maxsplit = 1)[1])
    #Handle !getideas calls
    elif message.content.startswith("!getideas "):
        getideas(message.content.split(" ", maxsplit = 1)[1], message.channel)
    #Handle idea deletion
    elif message.content.startswith("!delidea"):
        (m, num) = message.content.split(" ", maxsplit = 2)
        try:
            #Makes sure "1" points to d[userID][0]
            num = int(num) - 1
            if num < 0:
                num = num + 1
            #Grab the dictionary from the text file
            d = readfile()
            #Make sure the number is not greater than the amount of elements
            if (num + 1) > len(d[message.author.id]):
                client.send_message(message.channel, "The number you entered is too large. Please try again.")
            else:
                #Get rid of the element
                e = d[message.author.id].pop(num)
                #Rebuild the dictionary
                writedict(d)
                client.send_message(message.channel, "Idea `" + e.replace("`", "'") + "` deleted.")
        except:
            client.send_message(message.channel, "Invalid number. Please try again.")
    #Steal server info
    elif message.content.startswith("!machineinfo"):  
        client.send_message(message.channel, platform.node() + " " + platform.platform())
    #Reminders (currently disabled)
    elif message.content.startswith("!remind") and False:
        event = message.content.split(" ", maxsplit = 1)[1]
        (name, datetime) = event.split("@", maxsplit = 1)
        name = name.strip()
        dtime = dateparser.parse(datetime)
        s = sched.scheduler()
        s.enterabs(dtime.timestamp(), 1, (remind, message.channel), name)
        s.run()
    elif message.content.startswith("!killswitch"):
        #This should be more secure eventually
        sys.exit()
    elif message.content.startswith("!help"):
        client.send_message(message.channel, "PYBOT V5 HELP\n`!help` shows this page\n`!idea: <text>` Records a suggestion in your name. You can see it with !getideas\n`!getideas <username>` lists ideas from user\n`!delidea <n>` deletes the idea with the number n\n`!machineinfo` Returns server name and operating system")
@client.event
def on_ready():
    debug = client.get_channel(cfg.DEBUGCH)
    print(time.strftime("%Y-%m-%d %H:%M:%S") + ': Connected')
    client.send_message(debug, "Bot started")

client.run()
createLists()
