import os
import tempfile

import pytest
from service_discovery import create_app
from service_discovery.db import get_db, init_db


with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
     _data_sql = f.read().decode('utf8')

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class Registry(object):
    def __init__(self, client):
        self._client = client

    def list_entries(self):
        return self._client.get('/registry/list')
    
    def register(self, app_name, address, last_update):
        return self._client.post('/registry/register_instance', json={
            'app_name': app_name,
            'address': address,
            'last_update': last_update
        })

    def register_all(self, body=None):
        return self._client.post('/registry/register_all', json=body)

    def perform_update(self):
        return self._client.get('/registry/perform_update')


@pytest.fixture
def registry(client):
    return Registry(client)
