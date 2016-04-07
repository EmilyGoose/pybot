import discord, cfg, time

client = discord.Client()
debug = None
members = []
client.login(cfg.EMAIL, cfg.PASSWORD)

def createLists():
    for server in client.servers:
        for member in server.members:
            yield member
            userNames.append(member.name.lower())
            userIDs.append(member.id)

def logError(e):
    #Log unhandled exceptions
    try:
        f = open("log.txt", 'a')
    except:
        f = open("log.txt", 'w')
        f.close()
        f = open("log.txt", 'a')
    f.write("Unhandled exception occurred on " + time.strftime("%Y-%m-%d %H:%M:%S") + ":\n" + str(e) + "\n-----\n")
    f.close()

def logMiscError(t,e):
    #Log unhandled exceptions
    try:
        f = open("log.txt", 'a')
    except:
        f = open("log.txt", 'w')
        f.close()
        f = open("log.txt", 'a')
    f.write(str(t) + " occurred on " + time.strftime("%Y-%m-%d %H:%M:%S") + ":\n" + str(e) + "\n-----\n")
    f.close()

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

@client.event
def on_message(message):
    print(time.strftime("%Y-%m-%d %H:%M:%S") + ": " + message.author.name.title() + " says: " + message.content)
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        client.send_message(message.channel, 'Hello {}!'.format(message.author.mention()))
    #Handle new ideas
    if message.content.startswith('!idea:'):
        (m, idea) = message.content.split(": ", maxsplit = 1)
        dprotect = readfile()
        try:
            newidea(message.author.id, idea)          
        except Exception as e:
            client.send_message(message.channel, "Sorry, I couldn't add your idea. Please try again!")
            writedict(dprotect)
            logMiscError("Idea creation error", e)
        else:
            client.send_message(message.channel, "{}'s idea has been added.".format(message.author.mention()))
    #Handle !getideas calls
    elif message.content.startswith("!getideas "):
        (m, name) = message.content.split(" ", maxsplit = 1)
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
                    client.send_message(message.channel, s)
                else:
                    client.send_message(message.channel, name.title() + " has not entered any ideas yet!")
            else:
                client.send_message(message.channel, name.title() + " has not entered any ideas yet!")
        else:
            client.send_message(message.channel, "Name not found! Please try again!")
    #Handle idea deletion
    elif message.content.startswith("!delidea "):
        (m, num) = message.content.split(" ", maxsplit = 1)
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
            client.send(message.channel, "Invalid number. Please try again.")
    #Steal server info
    elif message.content.startswith("!machineinfo"):  
        client.send_message(message.channel, platform.node() + ' '.join(platform.dist()))
    #Uptime
    elif message.content.startswith("!uptime"):
        client.send_message(message.channel, "This instance of Pybot has been running for: " + time.strftime('%Hh%Mm%Ss', time.gmtime(time.time()-firststart)))  

@client.event
def on_ready():
    print(time.strftime("%Y-%m-%d %H:%M:%S") + ': Connected as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    debug = client.get_channel(cfg.DEBUGCH)
    client.send_message(debug, "Bot started")

client.run()
createLists()
