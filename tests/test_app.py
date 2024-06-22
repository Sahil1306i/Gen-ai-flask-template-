import pytest
from app import app, db, User, ReportData

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Add a test user
            user = User(username='testuser', password='testpass')
            db.session.add(user)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def test_login(test_client):
    response = test_client.post('/login', json={'username': 'testuser', 'password': 'testpass'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data

def test_generate_report(test_client):
    login_response = test_client.post('/login', json={'username': 'testuser', 'password': 'testpass'})
    token = login_response.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    response = test_client.post('/generate_report', json={'query': 'Generate a report'}, headers=headers)
    assert response.status_code == 200

def test_compile_report(test_client):
    login_response = test_client.post('/login', json={'username': 'testuser', 'password': 'testpass'})
    token = login_response.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    response = test_client.post('/compile_report', json={'report_spec': 'Sample report spec'}, headers=headers)
    assert response.status_code == 200
