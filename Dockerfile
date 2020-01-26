FROM ubuntu

MAINTAINER Tyler Stinson "tjstinso@gmail.com"

RUN apt-get update -y && apt-get install -y curl python3 python3-dev python3-pip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

RUN export FLASK_APP service_discovery

RUN flask init-db

RUN pytest

CMD . bin/startup.sh
