FROM ubuntu

MAINTAINER Tyler Stinson "tjstinso@gmail.com"

RUN apt-get update -y && apt-get install -y curl python3 python3-dev python3-pip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

COPY . /app

RUN pip3 install --no-cache-dir -r requirements.txt && \
export LC_ALL=C.UTF-8 && \
export LANG=C.UTF-8 && \
export FLASK_APP=service_discovery && \
python3 -m pytest && \
flask init-db


EXPOSE 8000

CMD . bin/startup.sh
