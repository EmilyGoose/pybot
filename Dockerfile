FROM alpine:3.1

# Update
RUN apk add --update python py-pip

# Install app dependencies
RUN apt-get install git
RUN pip install asyncio
RUN pip install requests
RUN pip install dateparser
RUN pip install wikipedia
RUN pip install github3.py
RUN pip install git+https://github.com/Rapptz/discord.py@async

# Bundle app source
COPY bot.py /src/bot.py

CMD ["python", "/src/bot.py"]
