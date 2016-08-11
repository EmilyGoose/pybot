import cfg, discord, asyncio, time

client = discord.Client()

@client.event
@asyncio.coroutine
def on_message(message):
    if message.content == "NUKETHEFUCKINGISSUES":
        server = client.get_server("184678944820297732")
        chanlist = []
        for channel in server.channels:
            chanlist.append(channel)
        for channel in chanlist:
            if channel.name.startswith("issue"):
                yield from client.delete_channel(channel)
        print("NUKED!")
                
@client.event
@asyncio.coroutine
def on_ready():
    print(time.strftime("%Y-%m-%d %H:%M:%S") + ': Connected to Discord')
        

client.run(cfg.TOKEN)
