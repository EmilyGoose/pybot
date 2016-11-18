FROM alpine:3.1

# Update
RUN apk add --update python py-pip

# Install app dependencies
RUN pip install -r requirements.txt

# Bundle app source
COPY bot.py /src/bot.py

CMD ["python", "/src/bot.py"]
