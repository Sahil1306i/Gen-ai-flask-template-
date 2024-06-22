import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_login(client):
    response = client.post('/login', json={'username': 'test', 'password': 'test'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data

def test_generate_report(client):
    login_response = client.post('/login', json={'username': 'test', 'password': 'test'})
    token = login_response.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/generate_report', json={'query': 'Generate a report'}, headers=headers)
    assert response.status_code == 200
  
