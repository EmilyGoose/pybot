# Bee Movie Automator

#Import all the stuff
import cfg, time
#Second line of import statements. These may need to be installed
import asyncio, discord

#Client intialization stuff
client = discord.Client()

print("Setup finished")
    

@client.event
@asyncio.coroutine
def on_message(message):
    print(time.strftime("%Y-%m-%d %H:%M:%S") + ": " + message.author.name + " says: " + message.content)
    if message.content.startswith("bee") and message.author.id == "143531770288013313":
        with open("beemovie.txt", 'r') as f:
            counter = 1
            for line in f:
                print(line)
                yield from client.send_message(message.channel, str(counter) + ": " + line, tts=True)
                time.sleep(1)
                counter += 1

@client.event
@asyncio.coroutine
def on_ready():
    print(time.strftime("%Y-%m-%d %H:%M:%S") + ': Connected to Discord')

client.run(cfg.TOKEN)
