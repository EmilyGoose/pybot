#Pybot discord-unstable build
#Misha Larionov and Nicholas Carr
#github.com/MishaLarionov/pybot/tree/discord-unstable

#TODO:
#Support multiple servers from one bot instance
#Add todo command

import discord, cfg, time, platform, ast, sched, sys, dateparser

#Client intialization stuff
client = discord.Client()
client.login(cfg.EMAIL, cfg.PASSWORD)

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
        #Or if an error happens. Possibly fixed.
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

def newidea(text, user, channel):
    try:
        #Grab the dictionary from the file
        dprotect = readfile()
        d = readfile()
        try:
            #Add the idea to the user's list of ideas
            d[user.id].append(text)
        except:
            #Create the user in the dictionary if they don't exist
            d[user.id] = [text]
        writedict(d)
        if readfile() == {}:
            debug("Something wiped the file. Restoring to previous version...")
            writedict(dprotect)
    except Exception as e:
        client.send_message(channel, "Sorry, I couldn't add your idea. Please try again!")
        writedict(dprotect)
    else:
        client.send_message(channel, "{}'s idea has been added.".format(user.mention()))

def getideas(name, channel):
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

def delidea(num, author, channel):
    try:
        #Makes sure "1" points to d[userID][0]
        num = int(num) - 1
        if num < 0:
            num = num + 1
        #Grab the dictionary from the text file
        d = readfile()
        #Make sure the number is not greater than the amount of elements
        if (num + 1) > len(d[author]):
            client.send_message(channel, "The number you entered is too large. Please try again.")
        else:
            #Get rid of the element
            e = d[author].pop(num)
            #Rebuild the dictionary
            writedict(d)
            client.send_message(channel, "Idea `" + e.replace("`", "'") + "` deleted.")
    except:
        client.send_message(channel, "Invalid number. Please try again.")

def setreminder():
    #Nicholas's uncommented reminder code
    event = message.content.split(" ", maxsplit = 1)[1]
    (name, datetime) = event.split("@", maxsplit = 1)
    name = name.strip()
    dtime = dateparser.parse(datetime)
    s = sched.scheduler()
    s.enterabs(dtime.timestamp(), 1, (remind, message.channel), name)
    s.run()

def processcommand(rawstring, channel, user):
    if " " in rawstring:
        (cmd, message) = rawstring.split(" ", maxsplit = 1)
        if cmd == "hello":
            client.send_message(channel, 'Hello {}!'.format(user.mention()))
        elif cmd == "idea" or cmd == "idea:":
            newidea(message, user, channel)
        elif cmd == "getideas":
            getideas(message, channel)
        elif cmd == "delidea":
            delidea(message, user.id, channel)
        elif cmd == "remind":
            #Code goes here someday
            pass
        elif cmd == "help":
            client.send_message(channel, "PYBOT V5 HELP\n`@pybot help` shows this page\n`@pybot idea: <text>` Records a suggestion in your name. You can see it with @pybot getideas\n`@pybot getideas <username>` lists ideas from user. *username* can be omitted to get your own ideas.\n`@pybot delidea <n>` deletes the idea with the number *n*\n`@pybot machineinfo` Returns server name and operating system")
    else:
        if rawstring == "hello":
            client.send_message(channel, 'Hello {}!'.format(user.mention()))
        if rawstring == "die" and user.name in ["ncarr", "Marsroverr"]:
            #This should be more secure eventually
            sys.exit()
        elif rawstring == "machineinfo":
            client.send_message(channel, platform.node() + " " + platform.platform())
        elif rawstring == "help":
            client.send_message(channel, "PYBOT V5 HELP\n`@pybot help` shows this page\n`@pybot idea: <text>` Records a suggestion in your name. You can see it with @pybot getideas\n`@pybot getideas <username>` lists ideas from user. *username* can be omitted to get your own ideas.\n`@pybot delidea <n>` deletes the idea with the number *n*\n`@pybot machineinfo` Returns server name and operating system")
        elif rawstring == "getideas":
            getideas(user.name, channel)

def remind(name, channel):
    client.send_message(channel, "You asked me to remind you to" + name)

def debug(text):
    if cfg.DEBUGCH:
        debug = client.get_channel(cfg.DEBUGCH)
        client.send_message(debug, text)

@client.event
def on_message(message):
    print(time.strftime("%Y-%m-%d %H:%M:%S") + ": " + message.author.name.title() + " says: " + message.content)    
    if message.author == client.user:
        return
    #if message.content.startswith("!") and len(message.content) > 1:
        #processcommand(message.content[1:], message.channel, message.author)
    if message.content.startswith("<@167668157224452097>") and len(message.content) > 22:
        processcommand(message.content[22:], message.channel, message.author)

@client.event
def on_ready():
    print(time.strftime("%Y-%m-%d %H:%M:%S") + ': Connected')

client.run()
createLists()
