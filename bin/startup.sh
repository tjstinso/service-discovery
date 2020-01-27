#!/bin/bash

gunicorn "service_discovery:create_app()" -w 1 --threads 8 -b "0.0.0.0:8000" &

while true
do
    curl 0.0.0.0:8000/registry/perform_update
    sleep 5
done
