import pytest
from app import app, get_db_connection
import sqlite3
import os

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Setup test DB
    if os.path.exists('database.db'):
        os.remove('database.db')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    cursor.execute("INSERT INTO users (id, username, password) VALUES (1, 'admin', 'secret123')")
    conn.commit()
    conn.close()

    with app.test_client() as client:
        yield client

    if os.path.exists('database.db'):
        os.remove('database.db')

def test_index(client):
    res = client.get('/')
    assert res.status_code == 200
    assert b"Vulnerable App running" in res.data

def test_valid_login(client):
    res = client.post('/login', json={'username': 'admin', 'password': 'secret123'})
    assert res.status_code == 200
    assert b"Welcome back" in res.data

def test_invalid_login(client):
    res = client.post('/login', json={'username': 'admin', 'password': 'wrong'})
    assert res.status_code == 401
