import re, time, cfg, ast, sys, importlib, slackclient, platform
from slackclient import SlackClient
from json import loads

#Initialize the bot class (useless for now)
class Bot:
    def __init__(self, token):
        self.token = token
        self.sc = SlackClient(token)

    def send(msgtext, msgchannel):
        self.sc.api_call("chat.postMessage", as_user="true:", channel=msgchannel, text=msgtext)

    def debug(msg):
        self.send("#pybotdebug", time.strftime("%Y-%m-%d %H:%M:%S") + ": " + msg)


#TODO: Move bot into a class and fix all the things
#TODO: Handle editing of messages
#TODO: Have bot ignore other bots

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

def logStart():
    #Log bot start
    try:
        f = open("log.txt", 'a')
    except:
        f = open("log.txt", 'w')
        f.close()
        f = open("log.txt", 'a')
    f.write("Bot started on " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n-----\n")
    f.close()

def logRestart():
    #Log bot restarts
    try:
        f = open("log.txt", 'a')
    except:
        f = open("log.txt", 'w')
        f.close()
        f = open("log.txt", 'a')
    f.write("Bot restarted on " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n-----\n")
    f.close()

def logShutdown():
    #Log bot shutdowns caused by too many exceptions
    try:
        f = open("log.txt", 'a')
    except:
        f = open("log.txt", 'w')
        f.close()
        f = open("log.txt", 'a')
    f.write("Bot shut down on " + time.strftime("%Y-%m-%d %H:%M:%S") + " due to too many unhandled exceptions.\n-----\n")
    f.close()

logStart()

while True:
    #No idea why this is here and not at the end
    importlib.reload(slackclient)
    
    starttime = time.time()
    
    print("Ready to connect to Slack.")

    #Initialize token for API calls
    token = cfg.USTOKEN
    sc = SlackClient(token)

    #Initialize empty lists
    userIDs = []
    userNames = []

    def readfile():
        #Initialize placeholder empty dictionary
        d = {}
        try:
            #Open the file
            with open("dict.txt", 'r') as f:
                #Iterate through the lines
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
        #Create placeholder empty string
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
            debug("Something wiped the file. Restoring to previous version...")
            writedict(dprotect)
        return()

    def createlists():
        #Get the user list
        #Removed str(), might put it back if something happens
        userlist = loads(sc.api_call("users.list").decode("utf-8"))['members']
        #Parse for user IDs
        for i in range(0, len(userlist)):
            userID = userlist[i]["id"]
            userIDs.append(userID)
            #Find the user's name
            try:
                userName = userlist[i]["profile"]["first_name"]
            except:
                #Find the user's username if they haven't set a name
                userName = userlist[i]["name"]
            userNames.append(userName.lower())
        return()

    def send(msgchannel, msgtext):
        sc.api_call("chat.postMessage", as_user="true:", channel=msgchannel, text=msgtext)

    def debug(msg):
        send("#pybotdebug", time.strftime("%Y-%m-%d %H:%M:%S") + ": " + msg)

    if sc.rtm_connect():
        print(time.strftime("%Y-%m-%d %H:%M:%S") + ": Connected to Slack.")
        debug("Bot (unstable version) started.")
        createlists()
        crashTimes = []
        timesCrashed = 0
        #Bot only runs for 2.5 hours before restarting
        while time.time() - starttime < 9000:
            try:
                #Get new information from the channel
                channelstatus = sc.rtm_read()
                if (channelstatus != []):
                    #Do literally everything
                    #Find the status type
                    statustype = channelstatus[0]["type"]
                    if statustype:
                        statustype = str(statustype).lower()
                        if statustype == "hello":
                            #Filter out hello message from server
                            print(time.strftime("%Y-%m-%d %H:%M:%S") + ": Hello message received from server.")
                        else:
                            #Find the user ID of the active user
                            try:
                                userID = channelstatus[0]["user"]
                            except:
                                debug("Unknown status! Here are the details:\n" + str(channelstatus))
                            else:
                                if not (userID == "U0H16CK8T" or userID == "USLACKBOT"):
                                    #Only run if the user is not pybot or Slackbot
                                    if statustype == "presence_change":
                                        #Handle presence changes
                                        presencestatus = channelstatus[0]["presence"]
                                        if userID in userIDs:
                                            userName = userNames[userIDs.index(userID)]
                                            print(time.strftime("%Y-%m-%d %H:%M:%S") + ": " + userName.title() + " is now " + presencestatus + ".")
                                        else:
                                            debug("User not found in list! Here are the details:\n" + str(channelstatus))
                                    elif statustype == "user_typing":
                                        #Handle typing
                                        if userID in userIDs:
                                            userName = userNames[userIDs.index(userID)]
                                            print(time.strftime("%Y-%m-%d %H:%M:%S") + ": " + userName + " is typing.")
                                        else:
                                            debug("User not found in list! Here are the details:\n" + str(channelstatus))
                                    elif statustype == "message":
                                        try:
                                            #Filter out 'messages' with a subtype
                                            #(Gets rid of bots)(should do edit as well)
                                            subtype = channelstatus[0]['subtype']
                                        except:
                                            if userID in userIDs:
                                                #Find where the user is in the lists
                                                userpos = userIDs.index(userID)
                                                #Find the user's name
                                                userName = userNames[userpos]
                                                #Get the full text of the message
                                                message = channelstatus[0]['text']
                                                message = message.strip()
                                                print(time.strftime("%Y-%m-%d %H:%M:%S") + ": " + userName.title() + " says: " + message)
                                                #Handle new ideas
                                                if (message.lower()[:9] == "us!idea: ") and (channelstatus[0]['channel'] == "G0H17UA5S"):
                                                    (m, idea) = message.split(": ", maxsplit = 1)
                                                    dprotect = readfile()
                                                    try:
                                                        newidea(userID, idea)          
                                                    except Exception as e:
                                                        send("#ideas", "Sorry, I couldn't add your idea. Please try again!")
                                                        writedict(dprotect)
                                                        logError(e)
                                                    else:
                                                        send("#ideas", userName.title() + "'s idea has been added.")
                                                #Handle !getideas calls
                                                elif (message.lower()[:12] == "us!getideas ") and (channelstatus[0]['channel'] == "G0H17UA5S"):
                                                    (m, name) = message.split(" ", maxsplit = 1)
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
                                                                s = ("Ideas for " + name.lower().title() + ":")
                                                                for i in range(0, len(d[userID])):
                                                                    s = (s + ("\n" + str(i+1) + ": " + d[userID][i]))
                                                                send("G0H17UA5S", s)
                                                            else:
                                                                send("G0H17UA5S", name.lower().title() + " has not entered any ideas yet!")
                                                        else:
                                                            send("G0H17UA5S", name.lower().title() + " has not entered any ideas yet!")
                                                    else:
                                                        send("G0H17UA5S", "Name not found! Please try again!")
                                                #Handle idea deletion
                                                elif (message.lower()[:11] == "us!delidea ") and (channelstatus[0]['channel'] == "G0H17UA5S"):
                                                    (m, num) = message.split(" ",maxsplit = 1)
                                                    try:
                                                        #Makes sure "1" points to d[userID][0]
                                                        num = int(num) - 1
                                                        if num < 0:
                                                            num = num + 1
                                                        #Grab the dictionary from the text file
                                                        d = readfile()
                                                        #Make sure the number is not greater than the amount of elements
                                                        if (num + 1) > len(d[userID]):
                                                            send("G0H17UA5S", "The number you entered is too large. Please try again.")
                                                        else:
                                                            #Get rid of the element
                                                            e = d[userID].pop(num)
                                                            #Rebuild the dictionary
                                                            writedict(d)
                                                            send("G0H17UA5S", "Idea `" + e.replace("`", "'") + "` deleted.")
                                                    except:
                                                        send("G0H17UA5S", "Invalid number. Please try again.")
                                                #Steal server info
                                                elif (message.lower()[:14] == "us!machineinfo") and (channelstatus[0]['channel'] == "G0H17UA5S"):  
                                                    send("G0H17UA5S", platform.node() + ' '.join(platform.dist()))
                                            else:
                                                debug("User not found in list! Here are the details:\n" + str(channelstatus) + "\nNote: User may have joined between bot restarts. Problem will be fixed next time bot restarts.")
                                    elif statustype == "reaction_added" or statustype == "reaction_removed":
                                        #Handle reactions and whatnot
                                        print(time.strftime("%Y-%m-%d %H:%M:%S") + ": Reaction added/removed somewhere. Too lazy to figure out where.")
                                    elif statustype == "user_change":
                                        #Rebuild userlist if someone changes their name
                                        print(time.strftime("%Y-%m-%d %H:%M:%S") + ": A user changed their profile info.")
                                        createlists()
                                    else:
                                        debug("Unimplemented status! Here are the details:\n" + str(channelstatus))
                                else:
                                    print(time.strftime("%Y-%m-%d %H:%M:%S") + ": Pybot and/or Slackbot did something.")
                    else:
                        debug("This error should never happen. Here are the details:\n" + str(channelstatus))
            except Exception as e:
                #Handle unhandled exceptions
                #Keep track of the number of exceptions
                timesCrashed += 1
                debug("Unhandled exception encountered. Restarting! (Exception #" + str(timesCrashed) + ", see log.txt for more info)")
                print(time.strftime("%Y-%m-%d %H:%M:%S") + ": Unhandled exception encountered. Restarting! (Exception #" + str(timesCrashed) + ", see log.txt for more info)")
                logError(e)
                #Create a list of exceptions, up to 10 
                crashTimes.append(time.time())
                if len(crashTimes) == 10:
                    if (crashTimes[9] - crashTimes[0]) > 60:
                        crashTimes.pop(0)
                    else:
                        try:
                            debug("Too many unhandled exceptions! Shutting down...")
                            logShutdown()
                        except:
                            pass
                        #Exit the program
                        sys.exit()
            time.sleep(1)
        debug("Bot running for over 2.5 hours. Restarting in 5 minutes.")
        logRestart()
        wait(300)
    else:
        #Handle being offline
        print("Pybot cannot connect to the internet. Please try again later.")
        #Kill the bot because the whole thing is in a while loop for some reason
        sys.exit()
