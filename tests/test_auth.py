import pytest
from fastapi.testclient import TestClient
from app.main import app
from uuid import uuid4

client = TestClient(app)

def unique_email():
    return f"user_{uuid4().hex[:8]}@example.com"

def unique_username(prefix="user"):
    return f"{prefix}_{uuid4().hex[:6]}"

def test_register_user():
    email = unique_email()
    username = unique_username("pedro")
    response = client.post("/register", json={
        "email": email,
        "username": username,
        "password": "pedro123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert data["username"] == username


def test_login_user():
    email = unique_email()
    username = unique_username("fatima")
    client.post("/register", json={
        "email": email,
        "username": username,
        "password": "fatima123"
    })
    
    response = client.post("/login", data={
        "username": email,  
        "password": "fatima123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_protected_endpoint():
    email = unique_email()
    username = unique_username("protected")
    register_response = client.post("/register", json={
        "email": email,
        "username": username,
        "password": "protectedpass123"
    })
    assert register_response.status_code == 201  
    
    login_response = client.post("/login", data={
        "username": email,
        "password": "protectedpass123"
    })
    assert login_response.status_code == 200  
    token = login_response.json()["access_token"]
    
    response = client.get("/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["username"] == username
