import sys
import pytest
from service_discovery.db import get_db


# INSERT INTO registry (address, app_name, last_update)
# VALUES ('0:0', 'self', 0), ('1:1', 'other', 0);


def test_get_registry(registry):
    data = registry.list_entries().get_json()
    assert '0:0' in data
    assert '1:1' in data

@pytest.mark.parametrize(('name', 'address', 'last'), (
    ('test1', '127.0.0.1:5000', 0),
))
def test_register_instance(registry, app, name, address, last):
    registry.register(name, address, last)

    with app.app_context():
        db = get_db()
        res = db.execute('SELECT * FROM registry WHERE address = ?', (address,)).fetchall()
        assert len(res) == 1
        db.close()

@pytest.mark.parametrize(('body'), (
    { 'self': {'app_name': 'self', 'last_update': 0} },
))
def test_register_all(registry, monkeypatch, body):
    called = False
    def fake_register(body, address, update):
        nonlocal called
        called = True
    monkeypatch.setattr('service_discovery.registry.register_instance', fake_register)
    res = registry.register_all(body)
    assert '200' in res.status
    assert called

def test_perform_update(registry, monkeypatch, app):
    out = []
    def fake_requests(url, data=None, json=None):
        out.append((url, data, json))
    monkeypatch.setattr('requests.post', fake_requests)
    registry.perform_update()
    register_self = out.pop(0) # ignore register single instance
    assert '/registry/register_instance' in register_self[0]
    assert register_self[1]['address'] == '127.0.0.1:{}'.format(app.config['PORT'])
    assert register_self[1]['app_name'] == app.config['APP_NAME']
    assert type(register_self[1]['last_update']) is int

    # compare urls
    import re
    for req in out:
        assert 'http://' in req[0] and '/registry/register_all' in req[0]
        assert req[1] == None
        for data in [i[2] for i in out]:
            for address in data:
                address_pattern = re.compile('(1:1|0:0)')
                name_pattern = re.compile('(self|other)')
                assert address_pattern.match(address)
                assert name_pattern.match(data[address]['app_name'])
                assert data[address]['last_update'] == 0


