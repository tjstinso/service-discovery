import os
import sys
from flask import Flask
from . import db
from . import registry

"""
TODOS
- app name must be injectable; P5
- create set of seed servers; P1
  - ideally not named localhost... P2
  - Probably want to setup docker to manage this in a more real world type scenario; P2
- create startup script that initialized the scheduled job; P2
- we should not be propagating our own IP address... someone else should know about this; P1
  - that is, we do not know our own IP address if we ask ourselves
"""


def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    service_name = '127.0.0.1'
    port = '8000'
    app.config.from_mapping(
        APP_NAME='service-discovery',
        PORT=port,
        SERVER_NAME="{}:{}".format(service_name, port),
        SERVICE_PORT=port,
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'service_discovery.sqlite'),
    )


    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return 'Welcome to the index of Service Discovery!'

    db.init_app(app)
    app.register_blueprint(registry.bp)
    return app
