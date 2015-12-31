import re, time, cfg, ast, sys, importlib, slackclient
from slackclient import SlackClient
from json import loads

while True:
    importlib.reload(slackclient)
    starttime = time.time()
    print("Ready to connect to Slack.")

    token = cfg.USTOKEN
    sc = SlackClient(token)

    userIDs = []
    userNames = []
    userchannels = []

    def readfile():
        #Initialize placeholder empty dictionary
        d = {}
        try:
            #Open the file
            with open("usdict.txt", 'r') as f:
                #Iterate through the lines
                for line in f:
                    #Grab the keys and values
                    (key, val) = line.split("|")
                    #Rebuild the dictionary
                    d[key] = ast.literal_eval(val)
        except:
            #Create a new file if it doesn't exist
            f = open("usdict.txt", 'w')
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
        f = open("usdict.txt", 'w')
        #Overwrite the file with the new content
        f.write(s)
        f.close()

    def newidea(name, text):
        #Grab the dictionary from the file
        d = readfile()
        text = text.strip()
        try:
            #Add the idea to the user's list of ideas
            d[name].append(text)
        except:
            #Create the user in the dictionary if they don't exist
            d[name] = [text]
        writedict(d)


    def createlists():
        #Get the user list
        userlist = loads(str(sc.api_call("users.list").decode("utf-8")))['members']
        #Parse for user IDs
        for i in range(0, len(userlist)):
            userID = userlist[i]["id"]
            userIDs.append(userID)
            #Find the user's name
            try:
                #Find the user's username if they haven't set a name
                userName = userlist[i]["profile"]["first_name"]
            except:
                userName = userlist[i]["name"]
            userNames.append(userName.lower())
        for n in range(0, len(userIDs)):
            #Find the DM channels for each user
            openstring = str((sc.api_call("im.open", user=userIDs[n])))
            searchObj = re.search(r'"id":"(.*?)"', openstring)
            userchannel = searchObj.group(1)
            userchannels.append(userchannel)
        return()

    def send(msgchannel, msgtext):
        sc.api_call("chat.postMessage", as_user="true:", channel=msgchannel, text=msgtext)

    def debug(msg):
        send("#pybotdebug", time.strftime("%Y-%m-%d %H:%M:%S") + ": " + msg)

    if sc.rtm_connect():
        print(time.strftime("%Y-%m-%d %H:%M:%S") + ": Connected to Slack.")
        createlists()
        debug("Bot (unstable version) started.")
        readfile()
        crashTimes = []
        timesCrashed = 0
        while True and (time.time() - starttime < 9000):
            try:
                #Get new information from the channel
                channelstatus = sc.rtm_read()
                if (channelstatus != []):
                    #Do literally everything
                    #Find the status type
                    statustype = channelstatus[0]["type"]
                    if statustype:
                        statustype = str(statustype)
                        if statustype == "hello":
                            #Filter out hello message from server
                            print(time.strftime("%Y-%m-%d %H:%M:%S") + ": Hello message received from server.")
                        else:
                            #Find the user ID of the active user
                            try:
                                userID = channelstatus[0]["user"]
                            except:
                                debug("Unknown status! Here are the details:\n" + str(channelstatus))
                            if not (userID == "U0H16CK8T" or userID == "USLACKBOT"):
                                #Only run if the user is not pybot or Slackbot
                                if statustype == "presence_change":
                                    #Handle presence changes
                                    presencestatus = channelstatus[0]["presence"]
                                    if userID in userIDs:
                                        userName = userNames[userIDs.index(userID)]
                                        print(time.strftime("%Y-%m-%d %H:%M:%S") + ": " + userName.title() + " is now " + presencestatus + ".")
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
                                        #(Gets rid of bots and edits)
                                        subtype = channelstatus[0]['subtype']
                                    except:
                                        if userID in userIDs:
                                            #Find where the user is in the lists
                                            userpos = userIDs.index(userID)
                                            #Find the user's name and channel
                                            userName = userNames[userpos]
                                            #Get the full text of the message
                                            message = channelstatus[0]['text']
                                            message.strip()
                                            print(time.strftime("%Y-%m-%d %H:%M:%S") + ": " + userName.title() + " says: " + message)
                                            #Handle new ideas
                                            if (message.lower()[:8] == "us!idea:") and (channelstatus[0]['channel'] == "G0H17UA5S"):
                                                (m, idea) = message.split(": ", maxsplit = 1)
                                                try:
                                                    newidea(userID, idea)
                                                    send("G0H17UA5S", userName.title() + "'s idea has been added.")
                                                except:
                                                    send("G0H17UA5S", "Sorry, I couldn't add your idea. Please try again!")
                                            #Handle !getideas calls
                                            elif (message.lower()[:11] == "us!getideas") and (channelstatus[0]['channel'] == "G0H17UA5S"):
                                                (m, name) = message.split (maxsplit = 1)
                                                #Check if the user exists
                                                if name.lower() in userNames:
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
                                            elif (message.lower()[:10] == "us!delidea") and (channelstatus[0]['channel'] == "G0H17UA5S"):
                                                (m, num) = message.split (maxsplit = 1)
                                                try:
                                                    #Makes sure "1" points to d[userID][0]
                                                    num = int(num) - 1
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
                                                        send("G0H17UA5S", "Idea `" + e + "` deleted.")
                                                except:
                                                    send("G0H17UA5S", "Invalid number. Please try again.")
                                        else:
                                            debug("User not found in list! Here are the details:\n" + str(channelstatus) + "\nNote: User may have joined between bot restarts. Problem will be fixed next time bot restarts.")
                                elif statustype == "reaction_added":
                                    print(time.strftime("%Y-%m-%d %H:%M:%S") + ": Reaction added somewhere. Too lazy to figure out where.")
                                else:
                                    debug("Unimplemented status! Here are the details:\n" + str(channelstatus))
                            else:
                                print(time.strftime("%Y-%m-%d %H:%M:%S") + ": Pybot and/or Slackbot did something.")
                    else:
                        debug("This error should never happen. Here are the details:\n" + str(channelstatus))
            except:
                timesCrashed += 1
                debug(time.strftime("%Y-%m-%d %H:%M:%S") + ": Unhandled exception encountered. Restarting! (Exception #" + str(timesCrashed) + ")")
                crashTimes.append(time.time())
                if len(crashTimes) == 10:
                    print(crashTimes)
                    if (crashTimes[9] - crashTimes[0]) > 60:
                        crashTimes.pop(0)
                    else:
                        try:
                            debug("Too many unhandled exceptions! Shutting down...")
                        except:
                            break
                        break
            time.sleep(0.5)
        debug("Program running for over 2.5 hours. Restarting!")
#Exit the program (Only happens if something bad happened)
sys.exit()
