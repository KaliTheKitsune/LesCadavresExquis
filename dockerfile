# syntax=docker/dockerfile:1

# python
FROM python:3.9-slim-buster

# maintainer
LABEL AUTHOR="Kali (https://github.com/KaliTheKitsune)"

# setup working directory
WORKDIR /app

# install deps
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# copy code
COPY . .

# run
CMD python3 -u main.py