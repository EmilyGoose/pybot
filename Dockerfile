
FROM alpine:3.4

# ensure local python is preferred over distribution python
ENV PATH /usr/local/bin:$PATH

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8

ENV PYTHON_VERSION 3.6.1

# if this is called "PIP_VERSION", pip explodes with "ValueError: invalid truth value '<VERSION>'"
ENV PYTHON_PIP_VERSION 9.0.1

# Install app dependencies

COPY requirements.txt /src/requirements.txt
RUN pip install -r requirements.txt

# Bundle app source
COPY bot.py /src/bot.py

CMD ["python3", "/src/bot.py"]
