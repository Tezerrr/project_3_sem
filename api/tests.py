from api.main import app, client
from api.models import User



def test_register():
    reg = client.post('/register', json={'username': 'TEST', 'email': 'TEST', 'password': 'TEST'})

    assert reg.status_code == 200


def test_login():
    log = client.post('/login', json={'email': 'TEST', 'password': 'TEST'})
    assert log.status_code == 200


def test_delete_user():
    log = client.post('/login', json={'email': 'TEST', 'password': 'TEST'})
    token = log.get_json()
    access_token = token['access_token']
    delete = client.delete('/delete', headers={'Authorization': f'Bearer {access_token}'})

    assert delete.status_code == 204