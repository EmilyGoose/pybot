from slackclient import SlackClient
import re, time, cfg, ast
from json import loads
print("Ready to connect to Slack.")

token = cfg.USTOKEN
sc = SlackClient(token)

userIDs = []
userNames = []
userchannels = []

def readfile():
    d = {}
    try:
        with open("usdict.txt", 'r') as f:
            for line in f:
                (key, val) = line.split("|")
                d[key] = ast.literal_eval(val)
    except:
        f = open("usdict.txt", 'w')
    f.close()
    return(d)

def writedict(d):
    s = ""
    keys = list(d.keys())
    for i in range(0, len(d)):
        s = (s + keys[i] + "|" + str(d[keys[i]]) + "\n")
    f = open("usdict.txt", 'w')
    f.write(s)
    f.close()

def newidea(name, text):
    d = readfile()
    try:
        d[name].append(text)
    except:
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
    send("#pybotdebug", msg)

if sc.rtm_connect():
    print("Connected to Slack.")
    createlists()
    debug("Bot (unstable version) started.")
    readfile()
    while True:
        #Get new information from the channel
        channelstatus = sc.rtm_read()
        if (channelstatus == []):
            #Discard empty channel status
            print("Nothing happened")
        else:
            #Do literally everything
            #Find the status type
            statustype = channelstatus[0]["type"]
            if statustype:
                statustype = str(statustype)
                if statustype == "hello":
                    #Filter out hello message from server
                    print("Hello message received from server.")
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
                                print(userName.title() + " is now " + presencestatus + ".")
                        elif statustype == "user_typing":
                            #Handle typing
                            if userID in userIDs:
                                userName = userNames[userIDs.index(userID)]
                                print(userName + " is typing.")
                            else:
                                debug("User not found in list! Here are the details:\n" + str(channelstatus))
                        elif statustype == "message":
                            if userID in userIDs:
                                #Find where the user is in the lists
                                userpos = userIDs.index(userID)
                                #Find the user's name and channel
                                userName = userNames[userpos]
                                userchannel = userchannels[userpos]
                                #This regex doesn't work if the message contains an apostrophe.
                                message = channelstatus[0]['text']
                                print(userName.title() + " says: " + message)
                                if channelstatus[0]['channel'] == userchannel:
                                    if message.lower()[:5] == "hello":
                                        send(userchannel, "Hi!")
                                if (message.lower()[:8] == "us!idea:") and (channelstatus[0]['channel'] == "G0H17UA5S"):
                                    (m, idea) = message.split(": ")
                                    try:
                                        newidea(userID, idea)
                                        send("G0H17UA5S", userName.title() + "'s idea has been added.")
                                    except:
                                        send("G0H17UA5S", "Sorry, I couldn't add your idea. Please try again!")
                                elif (message.lower()[:11] == "us!getideas") and (channelstatus[0]['channel'] == "G0H17UA5S"):
                                    (m, name) = message.split(" ")
                                    if name.lower() in userNames:
                                        userpos = userNames.index(name.lower())
                                        userID = userIDs[userpos]
                                        d = readfile()
                                        if userID in d:
                                            if len(d[userID]) > 0:
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
                                elif (message.lower()[:10] == "us!delidea") and (channelstatus[0]['channel'] == "G0H17UA5S"):
                                    (m, num) = message.split(" ")
                                    try:
                                        num = int(num) - 1
                                        d = readfile()
                                        if (num + 1) > len(d[userID]):
                                            send("G0H17UA5S", "The number you entered is too large. Please try again.")
                                        else:
                                            e = d[userID].pop(num)
                                            writedict(d)
                                            send("G0H17UA5S", "Idea `" + e + "` deleted.")
                                    except:
                                        send("G0H17UA5S", "Invalid number. Please try again.")
                            else:
                                debug("User not found in list! Here are the details:\n" + str(channelstatus) + "\nNote: User may have joined between bot restarts. Problem will be fixed next time bot restarts.")
                        else:
                            debug("Unimplemented status! Here are the details:\n" + str(channelstatus))
                    else:
                        print("Pybot and/or Slackbot did something.")
            else:
                debug("This error should never happen. Here are the details:\n" + str(channelstatus))
        time.sleep(0.5)
#'text': (["'])(.*?)\1
#print(sc.api_call("im.open", user=userID))
#'text': 'This is my legit "test" \'message\' with "lots" of \'quotation marks\''}]