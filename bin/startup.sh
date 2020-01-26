#!/bin/bash

gunicorn "service_discovery:create_app()" -w 1 --threads 8 &

while true
do
    curl 127.0.0.1:8000/registry/perform_update
    sleep 5
done
