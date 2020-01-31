from __future__ import print_function
import threading
import functools
import json
import time
import requests
from random import choice
from http.client import HTTPConnection

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
import sys
from service_discovery.db import get_db

bp = Blueprint('registry', __name__, url_prefix='/registry')

@bp.route('/list', methods=('GET',))
def get_registry(only_alive=False):
    db = get_db()
    data = db.execute('SELECT * from registry').fetchall()
    data = {
        d['address']: {
            i[0]: i[1] for i in zip(d.keys(), tuple(d)) if i[0] != 'address'
        } for d in data
    }
    return data, 200

@bp.route('/register_instance', methods=('POST',))
def register_instance(app_name=None, address=None, last_update=None):
    body = request.get_json()
    address = address or body['address']
    last_update = last_update or int(body['last_update'])
    app_name = app_name or body['app_name']
    db = get_db()
    try:
        if db.execute('SELECT * FROM registry WHERE address = ?', (address,)).fetchone():
            update = "UPDATE registry SET last_update = ? WHERE last_update < ? AND address = ?"
            try:
                db.execute(update, (last_update, last_update, address))
            except Exception as e:
                print("failed first commit", e)
        else:
            insert = "INSERT INTO registry (app_name, address, last_update) VALUES(?, ?, ?)"
            db.execute(insert, (app_name, address, last_update))
        db.commit()
    except Exception as e:
        print(e, file=sys.stdout)
        return str(e), 400
    return 'success', 200

@bp.route('/register_all', methods=('POST',))
def register_all():
    body = request.get_json()
    for address in body:
        register_instance(body[address]['app_name'], address, body[address]['last_update'])
    return 'Success!', 200

# these routing functions should be moved into another blueprint... but fine for now
@bp.route('/get_ip')
def get_ip():
    return request.remote_addr, 200

@bp.route('/perform_update')
def perform_update():
    neighbors, status = get_registry()
    neighbor = choice(list(neighbors))
    if 'ip' not in g: 
        ip = requests.get('http://{}/registry/get_ip'.format(neighbor)).text
        g.ip = ip
    else:
        ip = g.ip
    prefix = "http://{}/registry/register_".format(neighbor)
    if ip not in neighbors:
        neighbors[ip] = { 'app_name': current_app.config['APP_NAME'] }
    neighbors[ip]['last_update'] = int(time.time())
    requests.post(prefix + 'all', json=neighbors)
    return 'success', 200
