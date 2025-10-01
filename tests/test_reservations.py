import pytest
from datetime import datetime, timedelta
from uuid import uuid4

def unique_email():
    return f"user_{uuid4().hex[:8]}@example.com"

def unique_username(prefix="user"):
    return f"{prefix}_{uuid4().hex[:6]}"

def create_authenticated_user(client, prefix="test"):
    """Helper para crear usuario y obtener token"""
    email = unique_email()
    username = unique_username(prefix)
    
    client.post("/register", json={
        "email": email,
        "username": username,
        "password": "testpass123"
    })
    
    login = client.post("/login", data={
        "username": email,
        "password": "testpass123"
    })
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_reservation(client):
    headers = create_authenticated_user(client, "reserve")
    
    start = datetime.utcnow() + timedelta(hours=1)
    end = start + timedelta(hours=2)
    
    response = client.post("/reservations", 
        headers=headers,
        json={
            "space_name": "meeting_room_a",
            "start_datetime": start.isoformat(),
            "end_datetime": end.isoformat()
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["space_name"] == "meeting_room_a"
    assert data["status"] == "active"

def test_get_my_reservations(client):
    headers = create_authenticated_user(client, "getres")
    
    start = datetime.utcnow() + timedelta(hours=1)
    
    # Crear 2 reservas
    for i in range(2):
        client.post("/reservations", 
            headers=headers,
            json={
                "space_name": "desk_1",
                "start_datetime": (start + timedelta(days=i)).isoformat(),
                "end_datetime": (start + timedelta(days=i, hours=1)).isoformat()
            }
        )
    
    response = client.get("/reservations", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_update_reservation(client):
    headers = create_authenticated_user(client, "update")
    
    start = datetime.utcnow() + timedelta(hours=1)
    
    # Crear reserva
    create_response = client.post("/reservations", 
        headers=headers,
        json={
            "space_name": "meeting_room_a",
            "start_datetime": start.isoformat(),
            "end_datetime": (start + timedelta(hours=1)).isoformat()
        }
    )
    reservation_id = create_response.json()["id"]
    
    # Actualizar a otro espacio
    response = client.put(f"/reservations/{reservation_id}",
        headers=headers,
        json={"space_name": "meeting_room_b"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["space_name"] == "meeting_room_b"

def test_cancel_reservation(client):
    headers = create_authenticated_user(client, "cancel")
    
    start = datetime.utcnow() + timedelta(hours=1)
    
    # Crear reserva
    create_response = client.post("/reservations", 
        headers=headers,
        json={
            "space_name": "conference_hall",
            "start_datetime": start.isoformat(),
            "end_datetime": (start + timedelta(hours=2)).isoformat()
        }
    )
    reservation_id = create_response.json()["id"]
    
    # Cancelar (soft delete)
    response = client.delete(f"/reservations/{reservation_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"
    
    # Verificar que no aparece en lista de activas
    all_reservations = client.get("/reservations", headers=headers)
    assert len(all_reservations.json()) == 0
    
    # Pero sí aparece si incluimos canceladas
    with_cancelled = client.get("/reservations?include_cancelled=true", headers=headers)
    assert len(with_cancelled.json()) == 1

def test_user_cannot_access_other_user_reservation(client):
    # Usuario 1 crea reserva
    headers1 = create_authenticated_user(client, "user1")
    start = datetime.utcnow() + timedelta(hours=1)
    
    create_response = client.post("/reservations", 
        headers=headers1,
        json={
            "space_name": "desk_1",
            "start_datetime": start.isoformat(),
            "end_datetime": (start + timedelta(hours=1)).isoformat()
        }
    )
    reservation_id = create_response.json()["id"]
    
    # Usuario 2 intenta acceder a esa reserva
    headers2 = create_authenticated_user(client, "user2")
    response = client.get(f"/reservations/{reservation_id}", headers=headers2)
    
    assert response.status_code == 404  # No debe poder verla