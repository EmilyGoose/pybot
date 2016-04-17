#Pybot discord-unstable build
#Misha Larionov and Nicholas Carr
#github.com/MishaLarionov/pybot/tree/discord-unstable

#TODO:
#Support multiple servers from one bot instance
#Add todo command (Literally just a clone/rename of ideas)

#Import all the stuff, probably
import discord, cfg, time, platform, ast, sched, sys, os, dateparser

#Client intialization stuff
client = discord.Client()
client.login(cfg.EMAIL, cfg.PASSWORD)

def readfile(channel):
    #Function for grabbing the dictionary from the file
    d = {}
    #Open the file
    try:
        with open(channel.id + ".txt", 'r') as f:
            for line in f:
                #Grab the keys and values
                (key, val) = line.split("|", maxsplit = 1)
                #Rebuild the dictionary
                #Literally no clue how this line works
                d[key] = ast.literal_eval(val)
    except:
        try:
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

def writedict(d, channel):
    #Function to write the dictionary to the file
    s = ""
    #Get the keys to match them with index numbers
    keys = list(d.keys())
    for i in range(0, len(d)):
        #Write each line of the file with the proper syntax
        s = (s + keys[i] + "|" + str(d[keys[i]]) + "\n")
    try:
        f = open(channel.id + ".txt", 'w')
    except:
        f = open("dict.txt", 'w')
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
        writedict(dprotect, channel)
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
        d = readfile(channel)
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
        d = readfile(channel)
        #Make sure the number is not greater than the amount of elements
        if (num + 1) > len(d[author]):
            client.send_message(channel, "The number you entered is too large. Please try again.")
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
            #Write each line of the file with the proper syntax
            if keys[i] in d1:
                if keys[i] in d2:
                    s = (s + keys[i] + "|" + str(d1[keys[i]] + d2[keys[i]]) + "\n")
                else:
                    s = (s + keys[i] + "|" + str(d1[keys[i]]) + "\n")
            else:
                s = (s + keys[i] + "|" + str(d2[keys[i]]) + "\n")
            
        f2 = open("dict.txt", 'w')
        f2.write(s)
        f2.close()
        client.send_message(channel, "Successfully merged channel.")
    return()

def setreminder():
    #Nicholas's uncommented reminder code
    #I don't even think this function is ever called
    #It's not.
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
            client.send_message(channel, "PYBOT V5 HELP\n`@pybot help` shows this page\n`@pybot idea: <text>` Records a suggestion in your name. You can see it with @pybot getideas\n`@pybot getideas <username>` lists ideas from user. *username* can be omitted to get your own ideas.\n`@pybot delidea <n>` deletes the idea with the number *n*\n`@pybot machineinfo` Returns server name and operating system\n`@pybot splitchannel` Keeps future ideas from this channel separate from others, only accessible from the channel in which this command is run. Can be undone with `@pybot mergechannel`\n`@pybot mergechannel` Makes ideas from channel available to all channels; undoes `@pybot splitchannel`.")
    else:
        if rawstring == "hello":
            client.send_message(channel, 'Hello {}!'.format(user.mention()))
        if rawstring == "die" and user.name in ["ncarr", "Marsroverr"]:
            sys.exit()
        elif rawstring == "machineinfo":
            client.send_message(channel, platform.node() + " " + platform.platform())
        elif rawstring == "help":
            client.send_message(channel, "PYBOT V5 HELP\n`@pybot help` shows this page\n`@pybot idea: <text>` Records a suggestion in your name. You can see it with @pybot getideas\n`@pybot getideas <username>` lists ideas from user. *username* can be omitted to get your own ideas.\n`@pybot delidea <n>` deletes the idea with the number *n*\n`@pybot machineinfo` Returns server name and operating system\n`@pybot splitchannel` Keeps future ideas from this channel separate from others, only accessible from the channel in which this command is run. Can be undone with `@pybot mergechannel`\n`@pybot mergechannel` Makes ideas from channel available to all channels; undoes `@pybot splitchannel`.")
        elif rawstring == "getideas":
            getideas(user.name, channel)
        elif rawstring == "splitchannel":
            splitchannel(channel)
        elif rawstring == "mergechannel":
            mergechannel(channel)

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
    if message.content.startswith("<@167668157224452097>") and len(message.content) > 22:
        processcommand(message.content[22:], message.channel, message.author)
    elif message.content.startswith("@pybot") and len(message.content) > 7:
        processcommand(message.content[7:], message.channel, message.author)
    elif message.content == "<@167668157224452097>" or message.content == "@pybot":
        client.send_message(message.channel, 'Hello {}!'.format(message.author.mention()))

@client.event
def on_ready():
    print(time.strftime("%Y-%m-%d %H:%M:%S") + ': Connected')

client.run()
createLists()
