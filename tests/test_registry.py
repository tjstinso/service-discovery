import sys
import pytest
from service_discovery.db import get_db


# INSERT INTO registry (address, app_name, last_update)
# VALUES ('0:0', 'self', 0), ('1:1', 'other', 0);

def test_get_registry(registry):
    data = registry.list_entries().get_json()
    assert '0:0' in data
    assert '1:1' in data

@pytest.mark.parametrize(('name', 'address', 'last_update'), (
    ('test1', '127.0.0.1:5000', 0),
))
def test_register_instance(registry, app, name, address, last_update):
    registry.register(name, address, last_update)

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
    # before(app)
    out = {}
    def fake_requests(url, json=None):
        for i in [j for j in json if '1:1' in j or '0:0' in j]:
            out[i] = json[i]
    def fake_get_ip(url):
        class Text:
            text = '127.0.0.1'
        return Text()
    monkeypatch.setattr('requests.post', fake_requests)
    monkeypatch.setattr('requests.get', fake_get_ip)
    registry.perform_update()

    # compare urls
    import re
    for address in out:
        address_pattern = re.compile('(1:1|0:0)')
        name_pattern = re.compile('(self|other)')
        assert address_pattern.match(address)
        assert name_pattern.match(out[address]['app_name'])
        assert out[address]['last_update'] == 0
