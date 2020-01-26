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
    db.close()
    data = {
        d['address']: {
            i[0]: i[1] for i in zip(d.keys(), tuple(d)) if i[0] != 'address'
        } for d in data
    }
    return data, 200

@bp.route('/register_instance', methods=('POST',))
def register_instance(app_name=None, add=None, last_update=None):
    body = request.form
    db = get_db()
    try:
        address = add or body['address']
        update = "UPDATE registry SET last_update = ? WHERE last_update < ? AND address = ?"
        try:
            db.execute(update,
                       (last_update or int(body['last_update']),
                        last_update or int(body['last_update']),
                        address))
        except Exception as e:
            print("failed first commit", e)

        # untested
        if not db.execute('SELECT * FROM registry WHERE address = ?', (address,)).fetchone():
            insert = "INSERT INTO registry (app_name, address, last_update) VALUES(?, ?, ?)"
            db.execute(
                insert,
                (app_name or body['app_name'],
                 address,
                 last_update or int(body['last_update']))
            )
        db.commit()
    except Exception as e:
        print(e, file=sys.stdout)
        return e, 400
    db.close()
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
    ip, status = get_ip()
    # if '127.0.0.1' in neighbor: # that is looping back
    #     return 'Attempted to ping self', 200

    prefix = "http://{}/registry/register_".format(neighbor)
    requests.post(prefix + 'instance', data={
        'app_name': current_app.config['APP_NAME'], 'address': "{}:{}".format(ip, current_app.config['PORT']), 'last_update': int(time.time())
        }
    )
    requests.post(prefix + 'all', json=neighbors)
    return 'success', 200